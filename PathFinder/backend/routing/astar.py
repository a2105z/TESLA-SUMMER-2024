"""
EV-aware A* routing for EVNav.

State space:
    (node_id, soc_fraction)

Transitions:
- Drive along an outgoing edge if there is enough energy
- Optionally charge at charger nodes to increase SoC

This implementation is intentionally simple and tuned for the small
demo city graph, but the structure is production-style:
- Uses CostEngine for edge costs
- Tracks time, energy, and SoC along the route
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import heapq

from models.city_grid import CityGrid, NodeId
from models.vehicle import Vehicle
from .cost_engine import CostEngine, EdgeContext
from services.traffic_sim import TrafficSimulator


@dataclass
class RouteStep:
    node_id: NodeId
    soc: float  # 0–1
    cumulative_time_hours: float
    cumulative_energy_kwh: float
    is_charging_stop: bool = False


@dataclass
class RouteResult:
    steps: List[RouteStep]
    total_cost: float
    total_time_hours: float
    total_energy_kwh: float


def _soc_bucket(soc: float, resolution: float = 0.02) -> float:
    """
    Discretize SoC to avoid an explosion of nearly-identical states.

    resolution=0.02 → 2% buckets.
    """
    if soc < 0.0:
        soc = 0.0
    if soc > 1.0:
        soc = 1.0
    return round(soc / resolution) * resolution


def find_route(
    city: CityGrid,
    vehicle: Vehicle,
    start: NodeId,
    goal: NodeId,
    cost_engine: CostEngine,
    initial_soc: float = 1.0,
    traffic_sim: Optional[TrafficSimulator] = None,
) -> Optional[RouteResult]:
    """
    EV-aware A* search over (node, SoC).

    - Respects battery constraints: edges are only usable when SoC is sufficient.
    - Allows charging to full at charger nodes (with time penalty).
    - Uses CostEngine for edge costs; heuristic is 0 (Dijkstra-style) for now.
    """
    if start not in city.intersections or goal not in city.intersections:
        return None

    capacity = vehicle.battery_capacity_kwh
    start_soc = max(0.0, min(1.0, initial_soc))
    start_bucket = _soc_bucket(start_soc)

    # Priority queue entries: (f_cost, g_cost, node_id, soc, time_h, energy_kwh)
    frontier: List[Tuple[float, float, NodeId, float, float, float]] = []
    heapq.heappush(frontier, (0.0, 0.0, start, start_soc, 0.0, 0.0))

    # For each (node, soc_bucket) store best known g_cost (total_cost)
    best_cost: Dict[Tuple[NodeId, float], float] = {(start, start_bucket): 0.0}

    # Parent pointers for path reconstruction
    ParentKey = Tuple[NodeId, float]
    parents: Dict[ParentKey, Tuple[Optional[ParentKey], RouteStep]] = {}
    parents[(start, start_bucket)] = (None, RouteStep(node_id=start, soc=start_soc, cumulative_time_hours=0.0, cumulative_energy_kwh=0.0, is_charging_stop=False))

    while frontier:
        f_cost, g_cost, node_id, soc, time_h, energy_kwh = heapq.heappop(frontier)
        key = (node_id, _soc_bucket(soc))

        # If this is not the best known path for this state, skip it
        if best_cost.get(key, float("inf")) < g_cost - 1e-9:
            continue

        # Goal reached: reconstruct route
        if node_id == goal:
            steps: List[RouteStep] = []
            cur_key: Optional[ParentKey] = key
            # Note: the initial step stored in parents has cumulative_time=0, energy=0
            while cur_key is not None:
                parent_key, step = parents[cur_key]
                steps.append(step)
                cur_key = parent_key
            steps.reverse()
            return RouteResult(
                steps=steps,
                total_cost=g_cost,
                total_time_hours=time_h,
                total_energy_kwh=energy_kwh,
            )

        # --- 1) Driving transitions -----------------------------------------
        for seg in city.neighbors(node_id):
            # Skip edges blocked by incidents / accidents
            if traffic_sim is not None:
                mult = traffic_sim.traffic_multiplier(node_id, seg.end)
                if mult == float("inf"):
                    continue
            else:
                mult = 0.0
            # Energy required for this edge
            energy_required = vehicle.energy_for_distance(
                distance_km=seg.distance_km,
                elevation_gain_m=seg.elevation_gain_m,
            )
            available_energy = soc * capacity
            if energy_required > available_energy + 1e-9:
                # Not enough charge to traverse this segment
                continue

            next_energy = energy_kwh + energy_required
            next_soc = max(0.0, min(1.0, (available_energy - energy_required) / capacity))

            ctx = EdgeContext(
                distance_km=seg.distance_km,
                speed_limit_kph=seg.speed_limit_kph,
                elevation_gain_m=seg.elevation_gain_m,
                # Keep is_turn simple for now; refinements can consider geometry.
                is_turn=True,
                traffic_multiplier=mult,
            )
            dt = cost_engine.travel_time_hours(ctx)
            edge_cost = cost_engine.compute_cost(
                ctx,
                base_consumption_kwh_per_km=vehicle.base_consumption_kwh_per_km,
                uphill_penalty_kwh_per_m=vehicle.uphill_penalty_kwh_per_m,
            )

            new_time = time_h + dt
            new_cost = g_cost + edge_cost
            next_bucket = _soc_bucket(next_soc)
            next_key = (seg.end, next_bucket)

            if new_cost + 1e-9 < best_cost.get(next_key, float("inf")):
                best_cost[next_key] = new_cost
                # Heuristic h(n) is 0 for now (could use straight-line time later).
                heapq.heappush(frontier, (new_cost, new_cost, seg.end, next_soc, new_time, next_energy))
                parents[next_key] = (
                    key,
                    RouteStep(
                        node_id=seg.end,
                        soc=next_soc,
                        cumulative_time_hours=new_time,
                        cumulative_energy_kwh=next_energy,
                        is_charging_stop=False,
                    ),
                )

        # --- 2) Charging transition -----------------------------------------
        # Charge when battery is below 30% or if we have room to charge
        inter = city.intersections.get(node_id)
        MIN_CHARGE_THRESHOLD = 0.30  # Start charging below 30%
        if inter is not None and inter.has_charger and soc < 0.95:
            # Simple model: charge to full in one step.
            target_soc = 1.0
            delta_soc = target_soc - soc
            energy_added = delta_soc * capacity
            if energy_added > 0:
                # Charging time (hours) = energy (kWh) / power (kW)
                charge_time = energy_added / max(vehicle.max_charging_power_kw, 1e-3)
                # Charging contributes only time to the objective (no distance/turn).
                charge_cost = cost_engine.weights.alpha_time * charge_time

                new_time = time_h + charge_time
                new_cost = g_cost + charge_cost
                next_energy = energy_kwh  # driving energy; charging just refills the tank
                next_bucket = _soc_bucket(target_soc)
                next_key = (node_id, next_bucket)

                if new_cost + 1e-9 < best_cost.get(next_key, float("inf")):
                    best_cost[next_key] = new_cost
                    heapq.heappush(frontier, (new_cost, new_cost, node_id, target_soc, new_time, next_energy))
                    parents[next_key] = (
                        key,
                        RouteStep(
                            node_id=node_id,
                            soc=target_soc,
                            cumulative_time_hours=new_time,
                            cumulative_energy_kwh=next_energy,
                            is_charging_stop=True,
                        ),
                    )

    # No feasible route
    return None

