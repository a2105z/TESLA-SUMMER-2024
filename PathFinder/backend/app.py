"""
EVNav backend entrypoint.

Phases 2–5:
- Expose city / vehicle data
- Provide cost-engine-backed route scoring
- Implement EV-aware A* route planning with charging support
- Support traffic intensity and simulated accidents for rerouting demos
"""

from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.city_grid import CityGrid, create_demo_city
from models.vehicle import Vehicle, get_vehicle_presets
from routing.cost_engine import CostEngine, CostWeights, EdgeContext
from routing.astar import RouteResult, RouteStep, find_route
from routing.charger_planner import ChargingStop, plan_charging_stops
from services.traffic_sim import TrafficSimulator


app = FastAPI(
    title="EVNav",
    description="Energy-aware EV routing simulator backend.",
    version="0.2.0",
)

# Allow local frontends to talk to the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- In-memory demo data ----------------------------------------------------

DEMO_CITY: CityGrid = create_demo_city()
VEHICLE_PRESETS = get_vehicle_presets()
TRAFFIC_SIM = TrafficSimulator(base_intensity=0.0)


# --- Pydantic models for API -----------------------------------------------


class IntersectionOut(BaseModel):
    id: str
    name: str | None = None
    has_charger: bool
    lat: float | None = None
    lng: float | None = None


class RoadSegmentOut(BaseModel):
    start: str
    end: str
    distance_km: float
    speed_limit_kph: float
    elevation_gain_m: float
    road_class: str


class CityOut(BaseModel):
    intersections: List[IntersectionOut]
    segments: List[RoadSegmentOut]


class VehicleOut(BaseModel):
    id: str
    name: str
    battery_capacity_kwh: float
    base_consumption_kwh_per_km: float
    uphill_penalty_kwh_per_m: float
    max_charging_power_kw: float


class CostWeightsIn(BaseModel):
    alpha_time: float = 1.0
    beta_energy: float = 0.0
    gamma_turn: float = 0.0


class SegmentForScoring(BaseModel):
    distance_km: float
    speed_limit_kph: float
    elevation_gain_m: float = 0.0
    is_turn: bool = False
    traffic_multiplier: float = 0.0


class RouteScoreRequest(BaseModel):
    vehicle_id: str
    weights: CostWeightsIn
    segments: List[SegmentForScoring]


class SegmentScoreOut(BaseModel):
    index: int
    time_hours: float
    energy_kwh: float
    turn_penalty: float
    cost: float


class RouteScoreResponse(BaseModel):
    vehicle: VehicleOut
    weights: CostWeightsIn
    total_time_hours: float
    total_energy_kwh: float
    total_cost: float
    segments: List[SegmentScoreOut]


class RouteMode(str, Enum):
    FASTEST = "fastest"
    ENERGY_SAVER = "energy_saver"
    BALANCED = "balanced"


class RoutePlanRequest(BaseModel):
    start_node_id: str
    end_node_id: str
    vehicle_id: str
    mode: RouteMode = RouteMode.BALANCED
    initial_soc: float = 1.0


class RouteStepOut(BaseModel):
    node_id: str
    soc: float
    cumulative_time_hours: float
    cumulative_energy_kwh: float
    is_charging_stop: bool


class ChargingStopOut(BaseModel):
    node_id: str
    added_time_hours: float
    soc_after_charge: float


class RoutePlanResponse(BaseModel):
    mode: RouteMode
    vehicle: VehicleOut
    total_time_hours: float
    total_energy_kwh: float
    total_cost: float
    steps: List[RouteStepOut]
    charging_stops: List[ChargingStopOut]


class TrafficIntensityIn(BaseModel):
    intensity: float


class BlockEdgeIn(BaseModel):
    start_node_id: str
    end_node_id: str


class TrafficStateOut(BaseModel):
    intensity: float
    blocked_edges: List[BlockEdgeIn]


# --- Routes -----------------------------------------------------------------


@app.get("/health")
def health_check() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok", "service": "evnav"}


@app.get("/api/city", response_model=CityOut)
def get_city() -> CityOut:
    """Return the demo city graph (intersections + segments)."""
    city_dict = DEMO_CITY.to_dict()
    intersections = [IntersectionOut(**data) for data in city_dict["intersections"]]
    segments = [RoadSegmentOut(**data) for data in city_dict["segments"]]
    return CityOut(intersections=intersections, segments=segments)


@app.get("/api/vehicles", response_model=List[VehicleOut])
def get_vehicles() -> List[VehicleOut]:
    """Return the available EV presets."""
    return [VehicleOut(**v.as_dict()) for v in VEHICLE_PRESETS.values()]


@app.post("/api/route/score", response_model=RouteScoreResponse)
def score_route(payload: RouteScoreRequest) -> RouteScoreResponse:
    """
    Score a hypothetical route using the CostEngine.

    This does not perform pathfinding; instead the client provides
    a sequence of segments (distance, speed, elevation, turns, traffic).
    """
    vehicle: Vehicle | None = VEHICLE_PRESETS.get(payload.vehicle_id)
    if vehicle is None:
        raise ValueError(f"Unknown vehicle_id '{payload.vehicle_id}'")

    weights = CostWeights(
        alpha_time=payload.weights.alpha_time,
        beta_energy=payload.weights.beta_energy,
        gamma_turn=payload.weights.gamma_turn,
    )
    engine = CostEngine(weights=weights)

    segment_scores: List[SegmentScoreOut] = []
    total_time = 0.0
    total_energy = 0.0
    total_cost = 0.0

    for idx, seg in enumerate(payload.segments):
        ctx = EdgeContext(
            distance_km=seg.distance_km,
            speed_limit_kph=seg.speed_limit_kph,
            elevation_gain_m=seg.elevation_gain_m,
            is_turn=seg.is_turn,
            traffic_multiplier=seg.traffic_multiplier,
        )
        time_h = engine.travel_time_hours(ctx)
        energy_kwh = engine.energy_used_kwh(
            ctx,
            base_consumption_kwh_per_km=vehicle.base_consumption_kwh_per_km,
            uphill_penalty_kwh_per_m=vehicle.uphill_penalty_kwh_per_m,
        )
        turn_pen = engine.turn_penalty(ctx)
        cost = engine.compute_cost(
            ctx,
            base_consumption_kwh_per_km=vehicle.base_consumption_kwh_per_km,
            uphill_penalty_kwh_per_m=vehicle.uphill_penalty_kwh_per_m,
        )

        segment_scores.append(
            SegmentScoreOut(
                index=idx,
                time_hours=time_h,
                energy_kwh=energy_kwh,
                turn_penalty=turn_pen,
                cost=cost,
            )
        )
        total_time += time_h
        total_energy += energy_kwh
        total_cost += cost

    return RouteScoreResponse(
        vehicle=VehicleOut(**vehicle.as_dict()),
        weights=payload.weights,
        total_time_hours=total_time,
        total_energy_kwh=total_energy,
        total_cost=total_cost,
        segments=segment_scores,
    )


def _weights_for_mode(mode: RouteMode) -> CostWeights:
    """
    Map high-level mode names to concrete cost weights.
    These are tunable; current values are a reasonable starting point.
    """
    if mode == RouteMode.FASTEST:
        return CostWeights(alpha_time=1.0, beta_energy=0.1, gamma_turn=0.1)
    if mode == RouteMode.ENERGY_SAVER:
        return CostWeights(alpha_time=0.3, beta_energy=1.0, gamma_turn=0.05)
    # BALANCED
    return CostWeights(alpha_time=1.0, beta_energy=1.0, gamma_turn=0.1)


@app.post("/api/route/plan", response_model=RoutePlanResponse)
def plan_route(payload: RoutePlanRequest) -> RoutePlanResponse:
    """
    Plan an EV-aware route between two nodes.

    - Uses A* over (node, SoC)
    - Respects battery constraints and allows charging at charger nodes
    - Applies different cost weightings based on the selected mode
    """
    print(f"\n🚗 Route Planning Request:")
    print(f"   Start: {payload.start_node_id}")
    print(f"   End: {payload.end_node_id}")
    print(f"   Vehicle: {payload.vehicle_id}")
    print(f"   Mode: {payload.mode}")
    print(f"   Initial SoC: {payload.initial_soc}")
    
    if payload.start_node_id not in DEMO_CITY.intersections:
        raise HTTPException(status_code=400, detail=f"Unknown start node '{payload.start_node_id}'")
    if payload.end_node_id not in DEMO_CITY.intersections:
        raise HTTPException(status_code=400, detail=f"Unknown end node '{payload.end_node_id}'")

    vehicle: Vehicle | None = VEHICLE_PRESETS.get(payload.vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=400, detail=f"Unknown vehicle_id '{payload.vehicle_id}'")

    weights = _weights_for_mode(payload.mode)
    engine = CostEngine(weights=weights)

    result: RouteResult | None = find_route(
        city=DEMO_CITY,
        vehicle=vehicle,
        start=payload.start_node_id,
        goal=payload.end_node_id,
        cost_engine=engine,
        initial_soc=payload.initial_soc,
        traffic_sim=TRAFFIC_SIM,
    )
    if result is None or not result.steps:
        raise HTTPException(status_code=400, detail="No feasible route found with current battery and chargers.")
    
    print(f"\n✅ Route Found:")
    print(f"   Steps: {len(result.steps)}")
    print(f"   Node IDs: {[step.node_id for step in result.steps]}")
    print(f"   Total time: {result.total_time_hours:.2f}h")
    print(f"   Total energy: {result.total_energy_kwh:.2f} kWh")

    stops: List[ChargingStop] = plan_charging_stops(result.steps)

    steps_out: List[RouteStepOut] = [
        RouteStepOut(
            node_id=step.node_id,
            soc=step.soc,
            cumulative_time_hours=step.cumulative_time_hours,
            cumulative_energy_kwh=step.cumulative_energy_kwh,
            is_charging_stop=step.is_charging_stop,
        )
        for step in result.steps
    ]
    stops_out: List[ChargingStopOut] = [
        ChargingStopOut(
            node_id=stop.node_id,
            added_time_hours=stop.added_time_hours,
            soc_after_charge=stop.soc_after_charge,
        )
        for stop in stops
    ]

    return RoutePlanResponse(
        mode=payload.mode,
        vehicle=VehicleOut(**vehicle.as_dict()),
        total_time_hours=result.total_time_hours,
        total_energy_kwh=result.total_energy_kwh,
        total_cost=result.total_cost,
        steps=steps_out,
        charging_stops=stops_out,
    )


@app.get("/api/traffic", response_model=TrafficStateOut)
def get_traffic() -> TrafficStateOut:
    """Return current global traffic intensity and blocked edges."""
    blocked = [
        BlockEdgeIn(start_node_id=start, end_node_id=end)
        for (start, end) in TRAFFIC_SIM.blocked_edges
    ]
    return TrafficStateOut(intensity=TRAFFIC_SIM.base_intensity, blocked_edges=blocked)


@app.post("/api/traffic/intensity", response_model=TrafficStateOut)
def set_traffic_intensity(payload: TrafficIntensityIn) -> TrafficStateOut:
    """Update global traffic intensity (0–1)."""
    TRAFFIC_SIM.set_global_intensity(payload.intensity)
    return get_traffic()


@app.post("/api/traffic/block", response_model=TrafficStateOut)
def block_edge(payload: BlockEdgeIn) -> TrafficStateOut:
    """
    Simulate an accident by blocking a directed edge.
    The next routing request will avoid this edge.
    """
    if payload.start_node_id not in DEMO_CITY.intersections:
        raise HTTPException(status_code=400, detail=f"Unknown start node '{payload.start_node_id}'")
    if payload.end_node_id not in DEMO_CITY.intersections:
        raise HTTPException(status_code=400, detail=f"Unknown end node '{payload.end_node_id}'")
    TRAFFIC_SIM.block_edge(payload.start_node_id, payload.end_node_id)
    return get_traffic()


# Note: In development you would typically run this via:
#   uvicorn backend.app:app --reload

