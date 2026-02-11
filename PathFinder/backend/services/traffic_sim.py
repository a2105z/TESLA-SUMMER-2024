"""
Traffic simulation service for EVNav.

Phase 1: defines a minimal interface for obtaining traffic multipliers.
Later phases will incorporate:
- Time-of-day patterns
- Random incidents / accidents
- Integration with a UI slider for global intensity
"""

from typing import Dict, Tuple

from models.city_grid import NodeId


class TrafficSimulator:
    """
    Provides per-edge traffic multipliers.

    A multiplier of 0.0 means free flow; 0.5 means 50% slower; etc.
    """

    def __init__(self, base_intensity: float = 0.0) -> None:
        self.base_intensity = base_intensity
        # In later phases this will track incidents per edge.
        self.blocked_edges: set[Tuple[NodeId, NodeId]] = set()

    def set_global_intensity(self, intensity: float) -> None:
        """Update the global traffic level (0–1)."""
        self.base_intensity = max(0.0, min(1.0, intensity))

    def block_edge(self, start: NodeId, end: NodeId) -> None:
        """Mark a directed edge as blocked (used for 'Simulate Accident')."""
        self.blocked_edges.add((start, end))

    def is_blocked(self, start: NodeId, end: NodeId) -> bool:
        return (start, end) in self.blocked_edges

    def traffic_multiplier(self, start: NodeId, end: NodeId) -> float:
        """
        Return the traffic multiplier for an edge.

        For now this is just the global intensity unless the edge is blocked.
        """
        if self.is_blocked(start, end):
            # In the search logic we'll treat blocked edges as unusable,
            # but we keep this here for completeness.
            return float("inf")
        return self.base_intensity

