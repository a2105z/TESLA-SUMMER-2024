"""
Multi-objective cost engine for EVNav.

Core idea:
    cost = alpha * travel_time
         + beta  * energy_used
         + gamma * turn_penalty

This module is intentionally independent of any specific search algorithm.
An A* implementation will simply call into `compute_cost` for each edge.
"""

from dataclasses import dataclass


@dataclass
class CostWeights:
    """Weights for the different cost components."""

    alpha_time: float = 1.0
    beta_energy: float = 0.0
    gamma_turn: float = 0.0


@dataclass
class EdgeContext:
    """
    Context for a single edge traversal.

    Phase 1 keeps this minimal; later phases can add more.
    """

    distance_km: float
    speed_limit_kph: float
    elevation_gain_m: float
    is_turn: bool
    traffic_multiplier: float = 0.0  # 0 = free flow, 1 = 100% slower, etc.


class CostEngine:
    """Encapsulates the EVNav edge cost computation."""

    def __init__(self, weights: CostWeights | None = None) -> None:
        self.weights = weights or CostWeights()

    def travel_time_hours(self, ctx: EdgeContext) -> float:
        """Return travel time (hours) including traffic multiplier."""
        base_time = ctx.distance_km / max(ctx.speed_limit_kph, 1e-3)
        return base_time * (1.0 + ctx.traffic_multiplier)

    def energy_used_kwh(self, ctx: EdgeContext, base_consumption_kwh_per_km: float, uphill_penalty_kwh_per_m: float) -> float:
        """Return energy used (kWh) for this edge."""
        base = base_consumption_kwh_per_km * ctx.distance_km
        uphill = uphill_penalty_kwh_per_m * max(0.0, ctx.elevation_gain_m)
        return base + uphill

    def turn_penalty(self, ctx: EdgeContext) -> float:
        """Return a scalar penalty for turns."""
        return 1.0 if ctx.is_turn else 0.0

    def compute_cost(
        self,
        ctx: EdgeContext,
        base_consumption_kwh_per_km: float,
        uphill_penalty_kwh_per_m: float,
    ) -> float:
        """Compute the scalar cost for traversing an edge."""
        t = self.travel_time_hours(ctx)
        e = self.energy_used_kwh(ctx, base_consumption_kwh_per_km, uphill_penalty_kwh_per_m)
        turn = self.turn_penalty(ctx)

        return (
            self.weights.alpha_time * t
            + self.weights.beta_energy * e
            + self.weights.gamma_turn * turn
        )

