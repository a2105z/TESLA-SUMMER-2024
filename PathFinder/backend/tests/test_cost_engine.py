import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import math

from backend.routing.cost_engine import CostEngine, CostWeights, EdgeContext


def test_cost_engine_respects_energy_and_time_weights():
    weights = CostWeights(alpha_time=1.0, beta_energy=1.0, gamma_turn=0.0)
    engine = CostEngine(weights=weights)

    ctx_short = EdgeContext(
        distance_km=1.0,
        speed_limit_kph=60.0,
        elevation_gain_m=0.0,
        is_turn=False,
        traffic_multiplier=0.0,
    )
    ctx_long = EdgeContext(
        distance_km=2.0,
        speed_limit_kph=60.0,
        elevation_gain_m=0.0,
        is_turn=False,
        traffic_multiplier=0.0,
    )

    base_consumption = 0.2
    uphill_penalty = 0.0

    cost_short = engine.compute_cost(ctx_short, base_consumption, uphill_penalty)
    cost_long = engine.compute_cost(ctx_long, base_consumption, uphill_penalty)

    assert cost_long > cost_short


def test_cost_engine_turn_penalty_applied():
    weights = CostWeights(alpha_time=0.0, beta_energy=0.0, gamma_turn=1.0)
    engine = CostEngine(weights=weights)

    ctx_straight = EdgeContext(
        distance_km=1.0,
        speed_limit_kph=60.0,
        elevation_gain_m=0.0,
        is_turn=False,
        traffic_multiplier=0.0,
    )
    ctx_turn = EdgeContext(
        distance_km=1.0,
        speed_limit_kph=60.0,
        elevation_gain_m=0.0,
        is_turn=True,
        traffic_multiplier=0.0,
    )

    base_consumption = 0.2
    uphill_penalty = 0.0

    straight_cost = engine.compute_cost(ctx_straight, base_consumption, uphill_penalty)
    turn_cost = engine.compute_cost(ctx_turn, base_consumption, uphill_penalty)

    assert math.isclose(straight_cost, 0.0)
    assert math.isclose(turn_cost, 1.0)

