"""
City / road network model for EVNav.

Phase 2+ goal:
- Provide a realistic-enough in-memory city graph
- Include road classes, elevation, and charger locations
- Support real lat/lng coordinates
- Make it easy to serialize for the frontend
"""

from dataclasses import dataclass, asdict
from typing import Dict, List
import math


NodeId = str


@dataclass
class RoadSegment:
    """Represents a directed edge in the road network."""

    start: NodeId
    end: NodeId
    distance_km: float
    speed_limit_kph: float
    elevation_gain_m: float = 0.0
    road_class: str = "local"  # e.g. "highway", "arterial", "local"


@dataclass
class Intersection:
    """Logical node in the city graph."""

    id: NodeId
    name: str | None = None
    has_charger: bool = False
    lat: float | None = None
    lng: float | None = None


class CityGrid:
    """
    Lightweight container for the road network.

    In later phases this may load from JSON or a database.
    """

    def __init__(
        self,
        intersections: Dict[NodeId, Intersection] | None = None,
        adjacency: Dict[NodeId, List[RoadSegment]] | None = None,
    ) -> None:
        self.intersections: Dict[NodeId, Intersection] = intersections or {}
        self.adjacency: Dict[NodeId, List[RoadSegment]] = adjacency or {}

    def neighbors(self, node_id: NodeId) -> List[RoadSegment]:
        """Return outgoing road segments from the given node."""
        return self.adjacency.get(node_id, [])

    def all_segments(self) -> List[RoadSegment]:
        """Return a flat list of all road segments in the network."""
        segments: List[RoadSegment] = []
        for segs in self.adjacency.values():
            segments.extend(segs)
        return segments

    def to_dict(self) -> Dict[str, object]:
        """
        Serialize the city grid into a JSON-friendly dict.

        Intended for API responses.
        """
        return {
            "intersections": [asdict(inter) for inter in self.intersections.values()],
            "segments": [asdict(seg) for seg in self.all_segments()],
        }


def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance in km between two lat/lng points using Haversine formula.
    """
    R = 6371.0  # Earth radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def create_demo_city() -> CityGrid:
    """
    Create a realistic Chicago Loop road network with real coordinates.
    
    Covers major streets in the Loop bounded by:
    - North: Wacker Drive
    - South: Van Buren Street
    - East: Michigan Avenue
    - West: Wells Street
    
    Includes EV charging stations at strategic locations.
    """
    # Define all intersections with real Chicago Loop coordinates
    intersections: Dict[NodeId, Intersection] = {
        # Wacker & Michigan (northeast corner)
        "wacker_michigan": Intersection(
            id="wacker_michigan",
            name="Wacker & Michigan",
            has_charger=False,
            lat=41.8869,
            lng=-87.6246
        ),
        # Wacker & State
        "wacker_state": Intersection(
            id="wacker_state",
            name="Wacker & State",
            has_charger=False,
            lat=41.8869,
            lng=-87.6279
        ),
        # Wacker & Dearborn
        "wacker_dearborn": Intersection(
            id="wacker_dearborn",
            name="Wacker & Dearborn",
            has_charger=False,
            lat=41.8869,
            lng=-87.6298
        ),
        # Wacker & Clark
        "wacker_clark": Intersection(
            id="wacker_clark",
            name="Wacker & Clark",
            has_charger=True,  # Charging station
            lat=41.8869,
            lng=-87.6312
        ),
        # Wacker & LaSalle
        "wacker_lasalle": Intersection(
            id="wacker_lasalle",
            name="Wacker & LaSalle",
            has_charger=False,
            lat=41.8869,
            lng=-87.6328
        ),
        # Wacker & Wells
        "wacker_wells": Intersection(
            id="wacker_wells",
            name="Wacker & Wells",
            has_charger=False,
            lat=41.8869,
            lng=-87.6343
        ),
        
        # Lake & Michigan
        "lake_michigan": Intersection(
            id="lake_michigan",
            name="Lake & Michigan",
            has_charger=False,
            lat=41.8858,
            lng=-87.6246
        ),
        # Lake & State
        "lake_state": Intersection(
            id="lake_state",
            name="Lake & State",
            has_charger=False,
            lat=41.8858,
            lng=-87.6279
        ),
        # Lake & Dearborn
        "lake_dearborn": Intersection(
            id="lake_dearborn",
            name="Lake & Dearborn",
            has_charger=False,
            lat=41.8858,
            lng=-87.6298
        ),
        # Lake & Clark
        "lake_clark": Intersection(
            id="lake_clark",
            name="Lake & Clark",
            has_charger=False,
            lat=41.8858,
            lng=-87.6312
        ),
        # Lake & LaSalle
        "lake_lasalle": Intersection(
            id="lake_lasalle",
            name="Lake & LaSalle",
            has_charger=False,
            lat=41.8858,
            lng=-87.6328
        ),
        # Lake & Wells
        "lake_wells": Intersection(
            id="lake_wells",
            name="Lake & Wells",
            has_charger=False,
            lat=41.8858,
            lng=-87.6343
        ),
        
        # Randolph & Michigan
        "randolph_michigan": Intersection(
            id="randolph_michigan",
            name="Randolph & Michigan",
            has_charger=False,
            lat=41.8846,
            lng=-87.6246
        ),
        # Randolph & State
        "randolph_state": Intersection(
            id="randolph_state",
            name="Randolph & State",
            has_charger=False,
            lat=41.8846,
            lng=-87.6279
        ),
        # Randolph & Dearborn
        "randolph_dearborn": Intersection(
            id="randolph_dearborn",
            name="Randolph & Dearborn",
            has_charger=False,
            lat=41.8846,
            lng=-87.6298
        ),
        # Randolph & Clark
        "randolph_clark": Intersection(
            id="randolph_clark",
            name="Randolph & Clark",
            has_charger=False,
            lat=41.8846,
            lng=-87.6312
        ),
        # Randolph & LaSalle
        "randolph_lasalle": Intersection(
            id="randolph_lasalle",
            name="Randolph & LaSalle",
            has_charger=False,
            lat=41.8846,
            lng=-87.6328
        ),
        # Randolph & Wells
        "randolph_wells": Intersection(
            id="randolph_wells",
            name="Randolph & Wells",
            has_charger=False,
            lat=41.8846,
            lng=-87.6343
        ),
        
        # Washington & Michigan
        "washington_michigan": Intersection(
            id="washington_michigan",
            name="Washington & Michigan",
            has_charger=False,
            lat=41.8836,
            lng=-87.6246
        ),
        # Washington & State
        "washington_state": Intersection(
            id="washington_state",
            name="Washington & State",
            has_charger=True,  # Charging station
            lat=41.8836,
            lng=-87.6279
        ),
        # Washington & Dearborn
        "washington_dearborn": Intersection(
            id="washington_dearborn",
            name="Washington & Dearborn",
            has_charger=False,
            lat=41.8836,
            lng=-87.6298
        ),
        # Washington & Clark
        "washington_clark": Intersection(
            id="washington_clark",
            name="Washington & Clark",
            has_charger=False,
            lat=41.8836,
            lng=-87.6312
        ),
        # Washington & LaSalle
        "washington_lasalle": Intersection(
            id="washington_lasalle",
            name="Washington & LaSalle",
            has_charger=False,
            lat=41.8836,
            lng=-87.6328
        ),
        # Washington & Wells
        "washington_wells": Intersection(
            id="washington_wells",
            name="Washington & Wells",
            has_charger=False,
            lat=41.8836,
            lng=-87.6343
        ),
        
        # Madison & Michigan
        "madison_michigan": Intersection(
            id="madison_michigan",
            name="Madison & Michigan",
            has_charger=False,
            lat=41.8819,
            lng=-87.6246
        ),
        # Madison & State
        "madison_state": Intersection(
            id="madison_state",
            name="Madison & State",
            has_charger=False,
            lat=41.8819,
            lng=-87.6279
        ),
        # Madison & Dearborn
        "madison_dearborn": Intersection(
            id="madison_dearborn",
            name="Madison & Dearborn",
            has_charger=False,
            lat=41.8819,
            lng=-87.6298
        ),
        # Madison & Clark
        "madison_clark": Intersection(
            id="madison_clark",
            name="Madison & Clark",
            has_charger=False,
            lat=41.8819,
            lng=-87.6312
        ),
        # Madison & LaSalle
        "madison_lasalle": Intersection(
            id="madison_lasalle",
            name="Madison & LaSalle",
            has_charger=True,  # Charging station
            lat=41.8819,
            lng=-87.6328
        ),
        # Madison & Wells
        "madison_wells": Intersection(
            id="madison_wells",
            name="Madison & Wells",
            has_charger=False,
            lat=41.8819,
            lng=-87.6343
        ),
        
        # Monroe & Michigan
        "monroe_michigan": Intersection(
            id="monroe_michigan",
            name="Monroe & Michigan",
            has_charger=False,
            lat=41.8807,
            lng=-87.6246
        ),
        # Monroe & State
        "monroe_state": Intersection(
            id="monroe_state",
            name="Monroe & State",
            has_charger=False,
            lat=41.8807,
            lng=-87.6279
        ),
        # Monroe & Dearborn
        "monroe_dearborn": Intersection(
            id="monroe_dearborn",
            name="Monroe & Dearborn",
            has_charger=False,
            lat=41.8807,
            lng=-87.6298
        ),
        # Monroe & Clark
        "monroe_clark": Intersection(
            id="monroe_clark",
            name="Monroe & Clark",
            has_charger=False,
            lat=41.8807,
            lng=-87.6312
        ),
        # Monroe & LaSalle
        "monroe_lasalle": Intersection(
            id="monroe_lasalle",
            name="Monroe & LaSalle",
            has_charger=False,
            lat=41.8807,
            lng=-87.6328
        ),
        # Monroe & Wells
        "monroe_wells": Intersection(
            id="monroe_wells",
            name="Monroe & Wells",
            has_charger=False,
            lat=41.8807,
            lng=-87.6343
        ),
        
        # Adams & Michigan
        "adams_michigan": Intersection(
            id="adams_michigan",
            name="Adams & Michigan",
            has_charger=False,
            lat=41.8795,
            lng=-87.6246
        ),
        # Adams & State
        "adams_state": Intersection(
            id="adams_state",
            name="Adams & State",
            has_charger=False,
            lat=41.8795,
            lng=-87.6279
        ),
        # Adams & Dearborn
        "adams_dearborn": Intersection(
            id="adams_dearborn",
            name="Adams & Dearborn",
            has_charger=False,
            lat=41.8795,
            lng=-87.6298
        ),
        # Adams & Clark
        "adams_clark": Intersection(
            id="adams_clark",
            name="Adams & Clark",
            has_charger=False,
            lat=41.8795,
            lng=-87.6312
        ),
        # Adams & LaSalle
        "adams_lasalle": Intersection(
            id="adams_lasalle",
            name="Adams & LaSalle",
            has_charger=False,
            lat=41.8795,
            lng=-87.6328
        ),
        # Adams & Wells
        "adams_wells": Intersection(
            id="adams_wells",
            name="Adams & Wells",
            has_charger=True,  # Charging station
            lat=41.8795,
            lng=-87.6343
        ),
        
        # Jackson & Michigan
        "jackson_michigan": Intersection(
            id="jackson_michigan",
            name="Jackson & Michigan",
            has_charger=False,
            lat=41.8783,
            lng=-87.6246
        ),
        # Jackson & State
        "jackson_state": Intersection(
            id="jackson_state",
            name="Jackson & State",
            has_charger=False,
            lat=41.8783,
            lng=-87.6279
        ),
        # Jackson & Dearborn
        "jackson_dearborn": Intersection(
            id="jackson_dearborn",
            name="Jackson & Dearborn",
            has_charger=False,
            lat=41.8783,
            lng=-87.6298
        ),
        # Jackson & Clark
        "jackson_clark": Intersection(
            id="jackson_clark",
            name="Jackson & Clark",
            has_charger=False,
            lat=41.8783,
            lng=-87.6312
        ),
        # Jackson & LaSalle
        "jackson_lasalle": Intersection(
            id="jackson_lasalle",
            name="Jackson & LaSalle",
            has_charger=False,
            lat=41.8783,
            lng=-87.6328
        ),
        # Jackson & Wells
        "jackson_wells": Intersection(
            id="jackson_wells",
            name="Jackson & Wells",
            has_charger=False,
            lat=41.8783,
            lng=-87.6343
        ),
        
        # Van Buren & Michigan
        "vanburen_michigan": Intersection(
            id="vanburen_michigan",
            name="Van Buren & Michigan",
            has_charger=False,
            lat=41.8771,
            lng=-87.6246
        ),
        # Van Buren & State
        "vanburen_state": Intersection(
            id="vanburen_state",
            name="Van Buren & State",
            has_charger=True,  # Charging station
            lat=41.8771,
            lng=-87.6279
        ),
        # Van Buren & Dearborn
        "vanburen_dearborn": Intersection(
            id="vanburen_dearborn",
            name="Van Buren & Dearborn",
            has_charger=False,
            lat=41.8771,
            lng=-87.6298
        ),
        # Van Buren & Clark
        "vanburen_clark": Intersection(
            id="vanburen_clark",
            name="Van Buren & Clark",
            has_charger=False,
            lat=41.8771,
            lng=-87.6312
        ),
        # Van Buren & LaSalle
        "vanburen_lasalle": Intersection(
            id="vanburen_lasalle",
            name="Van Buren & LaSalle",
            has_charger=False,
            lat=41.8771,
            lng=-87.6328
        ),
        # Van Buren & Wells
        "vanburen_wells": Intersection(
            id="vanburen_wells",
            name="Van Buren & Wells",
            has_charger=False,
            lat=41.8771,
            lng=-87.6343
        ),
    }
    
    # Helper to create bidirectional road segments
    def add_bidirectional_road(
        adjacency: Dict[NodeId, List[RoadSegment]],
        id1: NodeId,
        id2: NodeId,
        speed_kph: float,
        road_class: str,
        elev_gain: float = 0.0
    ):
        """Add bidirectional road segments between two intersections."""
        inter1 = intersections[id1]
        inter2 = intersections[id2]
        dist = _haversine_distance(inter1.lat, inter1.lng, inter2.lat, inter2.lng)
        
        # Forward direction
        if id1 not in adjacency:
            adjacency[id1] = []
        adjacency[id1].append(RoadSegment(
            start=id1,
            end=id2,
            distance_km=dist,
            speed_limit_kph=speed_kph,
            elevation_gain_m=elev_gain,
            road_class=road_class
        ))
        
        # Reverse direction
        if id2 not in adjacency:
            adjacency[id2] = []
        adjacency[id2].append(RoadSegment(
            start=id2,
            end=id1,
            distance_km=dist,
            speed_limit_kph=speed_kph,
            elevation_gain_m=-elev_gain,
            road_class=road_class
        ))
    
    adjacency: Dict[NodeId, List[RoadSegment]] = {}
    
    # Build east-west streets (Wacker to Van Buren)
    ew_streets = [
        ("wacker", 48.0, "arterial"),
        ("lake", 48.0, "arterial"),
        ("randolph", 48.0, "arterial"),
        ("washington", 48.0, "arterial"),
        ("madison", 48.0, "arterial"),
        ("monroe", 48.0, "arterial"),
        ("adams", 48.0, "arterial"),
        ("jackson", 48.0, "arterial"),
        ("vanburen", 48.0, "arterial"),
    ]
    
    ns_avenues = ["michigan", "state", "dearborn", "clark", "lasalle", "wells"]
    
    for street, speed, road_class in ew_streets:
        for i in range(len(ns_avenues) - 1):
            id1 = f"{street}_{ns_avenues[i]}"
            id2 = f"{street}_{ns_avenues[i+1]}"
            add_bidirectional_road(adjacency, id1, id2, speed, road_class)
    
    # Build north-south avenues (Michigan to Wells)
    for avenue in ns_avenues:
        streets = ["wacker", "lake", "randolph", "washington", "madison", "monroe", "adams", "jackson", "vanburen"]
        # Michigan Ave is a major arterial
        speed = 56.0 if avenue == "michigan" else 48.0
        road_class = "arterial"
        
        for i in range(len(streets) - 1):
            id1 = f"{streets[i]}_{avenue}"
            id2 = f"{streets[i+1]}_{avenue}"
            # Small elevation changes for realism
            elev = 2.0 if i % 2 == 0 else -2.0
            add_bidirectional_road(adjacency, id1, id2, speed, road_class, elev)
    
    return CityGrid(intersections=intersections, adjacency=adjacency)
