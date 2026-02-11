"""
EV / battery model for EVNav.

Phase 2 goal:
- Provide realistic-enough EV presets
- Offer helpers to compute energy usage
- Be easy to serialize via the API
"""

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class Vehicle:
    """Simplified EV model."""

    id: str
    name: str
    battery_capacity_kwh: float
    base_consumption_kwh_per_km: float
    uphill_penalty_kwh_per_m: float
    max_charging_power_kw: float

    # 0–1 fraction of battery capacity
    soc: float = 1.0

    def energy_for_distance(
        self,
        distance_km: float,
        elevation_gain_m: float = 0.0,
    ) -> float:
        """Return estimated energy usage in kWh for a segment."""
        base = self.base_consumption_kwh_per_km * distance_km
        uphill = self.uphill_penalty_kwh_per_m * max(0.0, elevation_gain_m)
        return base + uphill

    def as_dict(self) -> Dict[str, object]:
        """JSON-friendly representation, suitable for API responses."""
        return asdict(self)


def get_vehicle_presets() -> Dict[str, "Vehicle"]:
    """
    Return Tesla vehicle catalog.

    Numbers are based on Tesla specifications for realistic simulation.
    """
    presets: Dict[str, Vehicle] = {
        "model_3_lr": Vehicle(
            id="model_3_lr",
            name="Model 3 Long Range",
            battery_capacity_kwh=75.0,
            base_consumption_kwh_per_km=0.16,  # ~160 Wh/km
            uphill_penalty_kwh_per_m=0.0004,
            max_charging_power_kw=250.0,  # Supercharger V3
        ),
        "model_s": Vehicle(
            id="model_s",
            name="Model S",
            battery_capacity_kwh=100.0,
            base_consumption_kwh_per_km=0.18,
            uphill_penalty_kwh_per_m=0.0005,
            max_charging_power_kw=250.0,
        ),
        "model_x": Vehicle(
            id="model_x",
            name="Model X",
            battery_capacity_kwh=100.0,
            base_consumption_kwh_per_km=0.21,  # Heavier SUV
            uphill_penalty_kwh_per_m=0.0006,
            max_charging_power_kw=250.0,
        ),
        "model_y": Vehicle(
            id="model_y",
            name="Model Y",
            battery_capacity_kwh=75.0,
            base_consumption_kwh_per_km=0.17,
            uphill_penalty_kwh_per_m=0.0005,
            max_charging_power_kw=250.0,
        ),
    }
    return presets

