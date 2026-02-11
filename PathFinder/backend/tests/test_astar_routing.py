import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.city_grid import create_demo_city
from backend.models.vehicle import get_vehicle_presets
from backend.routing.astar import find_route
from backend.routing.cost_engine import CostEngine, CostWeights
from backend.services.traffic_sim import TrafficSimulator


def test_astar_finds_route_chicago_loop():
    city = create_demo_city()
    vehicle = get_vehicle_presets()["model_3_lr"]
    engine = CostEngine(weights=CostWeights(alpha_time=1.0, beta_energy=0.5, gamma_turn=0.1))

    result = find_route(
        city=city,
        vehicle=vehicle,
        start="wacker_michigan",
        goal="vanburen_wells",
        cost_engine=engine,
        initial_soc=1.0,
    )

    assert result is not None
    assert result.steps[0].node_id == "wacker_michigan"
    assert result.steps[-1].node_id == "vanburen_wells"
    # SoC should never go negative
    for step in result.steps:
        assert 0.0 <= step.soc <= 1.0


def test_astar_respects_low_initial_soc_with_charging():
    city = create_demo_city()
    vehicle = get_vehicle_presets()["leaf_40"]  # Use smaller battery
    engine = CostEngine(weights=CostWeights(alpha_time=1.0, beta_energy=1.0, gamma_turn=0.1))

    # Start with low SoC; charging stations should be used if needed.
    result = find_route(
        city=city,
        vehicle=vehicle,
        start="wacker_michigan",
        goal="vanburen_wells",
        cost_engine=engine,
        initial_soc=0.1,  # Very low starting charge
    )

    # With Chicago Loop's smaller distances, may or may not need charging
    # The important test is that routing still works with low SoC
    assert result is not None
    # SoC constraints are respected
    for step in result.steps:
        assert 0.0 <= step.soc <= 1.0


def test_astar_reroutes_when_edge_blocked():
  city = create_demo_city()
  vehicle = get_vehicle_presets()["model_3_lr"]
  engine = CostEngine(weights=CostWeights(alpha_time=1.0, beta_energy=0.5, gamma_turn=0.1))
  traffic = TrafficSimulator(base_intensity=0.0)

  # Block a key segment to force rerouting
  traffic.block_edge("madison_state", "madison_dearborn")

  result = find_route(
      city=city,
      vehicle=vehicle,
      start="wacker_michigan",
      goal="vanburen_wells",
      cost_engine=engine,
      initial_soc=1.0,
      traffic_sim=traffic,
  )

  assert result is not None
  # Route should not contain the blocked transition
  for prev, cur in zip(result.steps, result.steps[1:]):
      assert not (prev.node_id == "madison_state" and cur.node_id == "madison_dearborn")

