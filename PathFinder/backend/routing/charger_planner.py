"""
Charging stop planning helpers for EVNav.

This module post-processes a computed route (from A*) to extract
human-friendly charging stop information:
- Where did we stop to charge?
- How much time was spent at each stop?
- What SoC did we have after each charge?
"""

from dataclasses import dataclass
from typing import List

from models.city_grid import NodeId
from routing.astar import RouteStep


@dataclass
class ChargingStop:
    node_id: NodeId
    added_time_hours: float
    soc_after_charge: float  # 0–1


def plan_charging_stops(steps: List[RouteStep]) -> List[ChargingStop]:
    """
    Extract charging stops from a list of RouteStep objects.

    Assumes:
    - RouteStep.is_charging_stop is True for the *post-charge* state
    - cumulative_time_hours is monotonically increasing
    """
    stops: List[ChargingStop] = []
    if not steps:
        return stops

    prev_time = 0.0
    for step in steps:
        if step.is_charging_stop:
            added_time = step.cumulative_time_hours - prev_time
            if added_time < 0:
                added_time = 0.0
            stops.append(
                ChargingStop(
                    node_id=step.node_id,
                    added_time_hours=added_time,
                    soc_after_charge=step.soc,
                )
            )
        prev_time = step.cumulative_time_hours

    return stops

