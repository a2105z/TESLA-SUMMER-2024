# Tesla Navigation – Energy-Aware Routing System

A production-style **Tesla navigation system** featuring real OpenStreetMap integration with Google Maps-style pan/zoom, address-based geocoding, energy-aware routing, Supercharger planning, and real-time traffic simulation.

---

## 🚗 Overview

EVNav is not a simple pathfinding visualizer—it's a **full-stack EV navigation prototype** that demonstrates:

- **Address-Based Routing**: Enter any address worldwide, geocoded via Nominatim (OpenStreetMap)
- **Interactive OpenStreetMap**: Real streets with Google Maps-style pan/zoom powered by Leaflet.js
- **Tesla Fleet**: Model 3, Model S, Model X, Model Y with accurate specifications
- **Energy-Aware A\* Routing**: Battery state-of-charge (SoC) constraints and consumption modeling
- **Multi-Objective Cost Engine**: Balances time, energy, and turn penalties
- **Supercharger Integration**: Automatic charging stop planning (250kW V3 Superchargers)
- **Three Routing Modes**: Fastest, Balanced, Energy Saver
- **Traffic Simulation**: Dynamic rerouting based on traffic intensity
- **Professional Tesla UI**: Dark theme, red accents, real map tiles, animated route visualization

---

## 🏗️ System Architecture

### Backend (Python / FastAPI)

```
backend/
├── app.py                    # FastAPI server with routing endpoints
├── models/
│   ├── city_grid.py          # Chicago Loop graph (54 nodes, ~200 edges)
│   └── vehicle.py            # EV models (Tesla Model 3, Nissan Leaf, VW ID.4)
├── routing/
│   ├── astar.py              # EV-aware A* over (node, SoC) state space
│   ├── cost_engine.py        # Multi-objective cost: α·time + β·energy + γ·turns
│   └── charger_planner.py    # Charging stop extraction & timing
├── services/
│   └── traffic_sim.py        # Traffic intensity + blocked edges (accidents)
└── tests/
    ├── test_cost_engine.py
    └── test_astar_routing.py
```

### Frontend (Vanilla JS + Leaflet)

```
frontend/
├── index.html                # Modern dark UI with Leaflet integration
├── css/styles.css            # Gradient buttons, Leaflet styling, side panels
└── js/
    ├── main.js               # Orchestration: API calls, UI events
    ├── api.js                # HTTP client for FastAPI backend
    ├── grid_renderer.js      # Leaflet map with OpenStreetMap tiles
    ├── route_animator.js     # Car icon animation on real map
    ├── soc_chart.js          # Canvas chart: SoC vs distance
    └── traffic_overlay.js    # Traffic intensity management
```

---

## 🌆 Chicago Loop Network

**Coverage:**
- **North:** Wacker Drive
- **South:** Van Buren Street  
- **East:** Michigan Avenue  
- **West:** Wells Street

**Major Streets (E-W):**  
Wacker, Lake, Randolph, Washington, Madison, Monroe, Adams, Jackson, Van Buren

**Major Avenues (N-S):**  
Michigan, State, Dearborn, Clark, LaSalle, Wells

**EV Charging Stations (5 locations):**
- Wacker & Clark
- Washington & State
- Madison & LaSalle
- Adams & Wells
- Van Buren & State

All intersections have **real lat/lng coordinates** and road segments use **calculated Haversine distances**.

---

## ⚡ Key Features

### 1. Energy-Aware Routing

Routes consider:
- Battery capacity (kWh)
- Base consumption (Wh/km)
- Elevation gain penalties
- Speed limits and traffic multipliers

The A\* search operates over **(node, SoC)** state space, rejecting moves that would exhaust the battery.

### 2. Multi-Objective Cost Engine

```
cost = α · travel_time + β · energy_used + γ · turn_penalty
```

Three routing modes:
- **Fastest**: prioritize time (α=1.0, β=0.1, γ=0.1)
- **Energy Saver**: minimize consumption (α=0.3, β=1.0, γ=0.05)
- **Balanced**: equal weight (α=1.0, β=1.0, γ=0.1)

### 3. Charging Stop Planning

When battery runs low:
- Identifies charger nodes along route
- Computes charging time: `(ΔSoC · capacity) / max_power_kW`
- Adds time penalty to route cost
- Shows charging stops in UI with SoC spikes on chart

### 4. Traffic & Rerouting

- **Traffic slider**: adjusts global traffic intensity (0–100%)
  - Roads color-coded: green → yellow → red
  - Route re-plans automatically with updated travel times
- **Simulate Accident**: blocks a mid-route segment
  - Forces immediate reroute via alternative path
  - Demonstrates real-time navigation behavior

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Modern web browser

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Backend (FastAPI)

```bash
# From PathFinder root
uvicorn backend.app:app --reload --port 8000
```

Backend runs on: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 3. Serve Frontend

```bash
cd frontend
python -m http.server 5500
```

Frontend runs on: `http://localhost:5500`

### 4. Open in Browser

Navigate to: `http://localhost:5500/index.html`

---

## 🎮 Demo Workflow

1. **Select Vehicle**: Choose from Tesla Model 3 LR, Nissan Leaf, or VW ID.4
2. **Pick Route**: Select start (e.g., `wacker_michigan`) and destination (e.g., `vanburen_wells`)
3. **Choose Mode**: Fastest / Balanced / Energy Saver
4. **Set Initial SoC**: Adjust battery level (20–100%)
5. **Plan Route**: Watch the car animate along the route
   - SoC chart shows battery depletion + charging spikes
   - Trip metrics: time, energy, #charges, current SoC
6. **Adjust Traffic**: Move slider → roads change color → route re-plans
7. **Simulate Accident**: Click button → mid-route blockage → automatic reroute

---

## 📊 API Endpoints

### Core Data

- `GET /api/city` → Chicago Loop intersections + road segments (with lat/lng)
- `GET /api/vehicles` → EV presets (Tesla, Nissan, VW)

### Routing

- `POST /api/route/plan`
  ```json
  {
    "start_node_id": "wacker_michigan",
    "end_node_id": "vanburen_wells",
    "vehicle_id": "model_3_lr",
    "mode": "balanced",
    "initial_soc": 0.8
  }
  ```
  Returns: `{ steps, total_time_hours, total_energy_kwh, charging_stops }`

### Traffic Control

- `GET /api/traffic` → Current intensity + blocked edges
- `POST /api/traffic/intensity` → Update global traffic (0–1)
- `POST /api/traffic/block` → Block edge (simulate accident)

---

## 🧪 Testing

Run backend tests:

```bash
cd backend
pytest tests/
```

Tests cover:
- Cost engine correctness (time, energy, turn penalties)
- EV-aware A\* (finds feasible routes, respects SoC)
- Charging integration (low SoC triggers charging stops)
- Rerouting (blocked edges force alternative paths)

---

## 🎨 UI Highlights

- **Tesla-inspired dark theme** with cyan/blue gradients
- **SVG map projection** from real lat/lng → screen coordinates
- **Live SoC chart** (Canvas): battery % vs cumulative distance
- **Animated car icon** with real-time SoC updates
- **Road color overlay** for traffic visualization
- **Side panel metrics**: time, energy, charges, route steps

---

## 🔮 Future Enhancements

- **Real map tiles**: Integrate Leaflet + OpenStreetMap basemap
- **Expanded network**: Cover entire downtown Chicago or multiple cities
- **Time-of-day traffic**: Peak/off-peak patterns
- **Weather impact**: Rain/snow affecting consumption
- **Multi-vehicle comparison**: Side-by-side route analysis

---

## 📝 License

MIT License - feel free to use for learning, portfolios, or demos.

---

## 👨‍💻 Author

Built as a demonstration of production-style system architecture, clean separation of concerns, and real-world EV routing constraints—not just a classroom pathfinding demo.

**Tech stack**: Python (FastAPI), JavaScript (ES6 modules), SVG rendering, Canvas charts, Haversine distance calculations, A\* search with constraints.

