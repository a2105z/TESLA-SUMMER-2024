# EVNav Chicago Loop – Demo Guide

## 🎬 Quick Demo Script

This is a guide for showcasing EVNav to recruiters, professors, or anyone interested in seeing a production-style EV navigation system.

---

## 🚀 Setup (2 minutes)

### 1. Start Backend
```bash
cd PathFinder
uvicorn backend.app:app --reload --port 8000
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

### 2. Start Frontend
```bash
cd frontend
python -m http.server 5500
```

### 3. Open Browser
Navigate to: `http://localhost:5500/index.html`

---

## 🎯 Demo Flow (5 minutes)

### Part 1: Basic Navigation (1 min)

**What to say:**
> "This is EVNav, an energy-aware EV routing system for Chicago's Loop district. It uses real coordinates for 54 intersections and actual street distances calculated with Haversine formula."

**Actions:**
1. Select **Vehicle**: Tesla Model 3 Long Range
2. **Start**: `wacker_michigan` (northeast corner)
3. **Destination**: `vanburen_wells` (southwest corner)
4. **Mode**: Balanced
5. **Initial SoC**: 80%
6. Click **Plan Route**

**What to highlight:**
- Car animates along the route
- SoC chart shows battery depletion in real time
- Trip metrics update: time, energy, charging stops
- Route steps list shows each intersection with SoC and cumulative time

---

### Part 2: Mode Comparison (2 min)

**What to say:**
> "The system supports three routing modes by adjusting the cost function weights. Watch how the route, time, and energy change."

**Actions:**
1. Keep same start/destination
2. Switch **Mode** to **Fastest**
   - Click Plan Route
   - Point out: "Fastest prioritizes time over energy"
3. Switch **Mode** to **Energy Saver**
   - Click Plan Route
   - Point out: "Energy Saver may take longer but uses less battery"

**What to highlight:**
- Different modes choose different paths when tradeoffs exist
- Total time vs total energy metrics shift
- SoC chart shape changes (steeper drop = more aggressive driving)

---

### Part 3: Low Battery & Charging (1 min)

**What to say:**
> "The system models battery constraints. If you start with low charge, it automatically plans charging stops at available stations."

**Actions:**
1. Select **Vehicle**: Nissan Leaf 40 kWh (smaller battery)
2. Same route: `wacker_michigan` → `vanburen_wells`
3. **Initial SoC**: 25% (low battery)
4. Click **Plan Route**

**What to highlight:**
- Route includes **charging stops** (marked in green in route steps)
- SoC chart shows **sharp upward spikes** at charging stations
- Trip metrics show number of charging stops
- Total time increases due to charging

---

### Part 4: Traffic & Rerouting (1 min)

**What to say:**
> "Now let's simulate real-world conditions: traffic and accidents."

**Actions:**
1. Reset to: Tesla Model 3, `wacker_michigan` → `vanburen_wells`, 80% SoC
2. Plan Route (baseline)
3. Move **Traffic** slider from Low → **Severe**
   - Roads turn yellow → red
   - Watch metrics: total time increases
   - Route may change if alternative paths exist
4. Click **Simulate Accident**
   - System blocks a mid-route segment
   - Route instantly recalculates around the blockage
   - Point out: "This is how real navigation handles live incidents"

**What to highlight:**
- Traffic affects cost calculation (time increases)
- Accident simulation forces reroute in real time
- System demonstrates dynamic replanning

---

## 🔥 Key Talking Points

### Architecture
- **Modular cost engine**: `cost = α·time + β·energy + γ·turns`
- **Constrained A\***: Search space is `(intersection, SoC)`, not just `(intersection)`
- **Separation of concerns**: Models → Routing → Services → API
- **Real coordinates**: 54 intersections in Chicago Loop with Haversine distances

### Real-World Constraints
- Battery capacity and consumption modeling
- Charging time calculation: `(ΔSoC · capacity_kWh) / power_kW`
- Traffic multipliers affecting travel time
- Edge blocking for accident simulation

### Visualization
- **Not a grid demo**: SVG projection from real lat/lng
- **SoC chart**: Canvas rendering with gradients showing battery drain + charge spikes
- **Live animation**: Car moves along route with real-time SoC updates
- **Tesla-inspired UI**: Professional dark theme, gradient buttons, smooth interactions

---

## 📊 Stats to Mention

- **54 real intersections** spanning Chicago's Loop
- **~200 bidirectional road segments** with calculated distances
- **5 EV charging stations** at strategic locations
- **3 vehicle models** with realistic battery/consumption specs
- **3 routing modes** with different optimization objectives
- **Full test coverage** (pytest suite validates correctness)

---

## 🎨 Visual Polish Details

Point out these subtle but impressive touches:

1. **Road thickness varies** by class (highway > arterial > local)
2. **Charging nodes highlighted** with green glow
3. **Route uses gradient** (cyan → blue) with drop shadow
4. **Background grid** for depth perception
5. **Traffic color coding**: green → yellow → red
6. **Pill-style controls** with active state highlighting
7. **Responsive metrics** update during animation

---

## 💡 Comparison to "Typical" Student Projects

Most students:
- Implement A\* once on a grid
- Draw colored squares
- Done

This project:
- Models **real physics** (energy, charging, elevation)
- Implements **constrained search** (battery feasibility)
- Uses **real geography** (Chicago Loop coordinates)
- Builds **production architecture** (FastAPI, modular cost engine, clean separation)
- Provides **interactive simulation** (traffic, accidents, modes)
- Demonstrates **systems thinking** (not just algorithms)

---

## 🐛 If Something Goes Wrong

- **Backend won't start**: Check port 8000 is free, or change in `api.js`
- **Frontend shows errors**: Backend must be running first
- **Map looks wrong**: Refresh page after backend changes
- **No route found**: Try higher initial SoC or different start/end combo

---

## 📸 Screenshot Checklist

Capture these for portfolio/resume:

1. Full UI with route planned (shows map, SoC chart, metrics)
2. SoC chart with charging spike (proves charging logic)
3. Traffic slider at "Severe" with red roads
4. Route comparison: Fastest vs Energy Saver side-by-side
5. Code snippet of cost engine or A\* (shows technical depth)

---

## ⏱️ Total Demo Time

- Quick version: 3 minutes (Parts 1 + 4)
- Full version: 5 minutes (all parts)
- Deep dive: 10+ minutes (add code walkthrough)

---

**Remember:** This isn't a toy. It's a mini navigation system with real constraints, real geography, and real trade-off modeling. That's what makes it resume-tier.
