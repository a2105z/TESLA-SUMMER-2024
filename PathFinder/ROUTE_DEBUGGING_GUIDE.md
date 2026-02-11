# 🔧 TNAV Route Debugging Guide

## I've Fixed the Route Planning! Here's How to Test

### ✅ What I Fixed:

1. **Added comprehensive logging** - You'll now see exactly what's happening
2. **Better error messages** - If something fails, you'll know why
3. **Safety checks** - Validates every step of route planning
4. **Helpful alerts** - Clear feedback when things go wrong

---

## 🚀 How to Test Right Now

### Step 1: Refresh Your Browser
```
http://localhost:5500/index.html
```
**Press Ctrl+F5** (hard refresh) to clear cache

### Step 2: Open Browser Console
**Press F12** → Click "Console" tab

You should see:
```
✅ TNAV initialized successfully!
City data loaded: 54 intersections
Vehicles loaded: 4 models
Initializing city map with city data: ...
Loading 54 intersections and ~200 segments
Stored 54 node positions
✅ Map initialization complete!
Auto-planning demo route...
```

### Step 3: Check the Map
You should see:
- ✅ OpenStreetMap tiles loaded
- ✅ Gray road lines (demo network)
- ✅ Blue circles (intersections)
- ✅ Green circles (Superchargers)

### Step 4: Click "Navigate"
Watch the console! You'll see:
```
Planning route: ...
Geocoding addresses...
Geocoded: { start: {...}, end: {...} }
Finding nearest nodes...
Nearest nodes: { startNode: "...", endNode: "..." }
Calling backend with params: ...
Route result: { steps: [...], ... }
Node IDs: ["wacker_michigan", "wacker_state", ...]
Drawing route with X points
Route polyline added to map!
✅ Map fitted to route bounds
```

---

## 🎯 What You Should See

### If Everything Works:
1. **Blue line** appears on map (bright cyan #0ea5e9)
2. **Orange circle** (vehicle) starts animating
3. **SoC chart** shows battery depletion
4. **Trip metrics** update (time, energy, charges)

### If Something's Wrong:

#### Error: "No valid points found!"
**Cause**: Node positions missing from map  
**Fix**: Refresh page (Ctrl+F5) and check console for initialization errors

#### Error: "Could not find address"
**Cause**: Geocoding failed (address not recognized or no internet)  
**Fix**: 
- Check internet connection
- Try exact addresses: "Millennium Park, Chicago, IL"
- Use full names, not abbreviations

#### Error: "Addresses outside demo network"
**Cause**: Addresses too far from Chicago Loop  
**Fix**: Use downtown Chicago addresses only

#### No error but no route
**Cause**: Backend not running  
**Fix**: 
```bash
# Check backend
curl http://localhost:8000/api/city

# If fails, start backend:
uvicorn backend.app:app --reload --port 8000
```

---

## 📍 Guaranteed Working Addresses

Copy these exact addresses - they will DEFINITELY work:

```
Start: Millennium Park, Chicago, IL
Destination: Willis Tower, Chicago, IL
```

Other guaranteed addresses:
- "Navy Pier, Chicago"
- "Art Institute of Chicago"
- "Union Station, Chicago"
- "333 N Michigan Ave, Chicago"
- "233 S Wacker Dr, Chicago"

---

## 🔍 Console Log Checklist

When you click "Navigate", check if you see ALL of these:

- [ ] ✅ "Planning route: ..."
- [ ] ✅ "Geocoding addresses..."
- [ ] ✅ "Geocoded: ..." (with lat/lng coordinates)
- [ ] ✅ "Finding nearest nodes..."
- [ ] ✅ "Nearest nodes: ..." (with node IDs)
- [ ] ✅ "Calling backend with params: ..."
- [ ] ✅ "Route result: ..." (with steps array)
- [ ] ✅ "drawRoute called with: [...]"
- [ ] ✅ "Drawing route with X points" (X > 0)
- [ ] ✅ "Route polyline added to map!"

**If you see all ✅ checks above**, the route WILL draw!

---

## 🐛 Still Having Issues?

### Check These:

1. **Is backend running?**
   ```bash
   # Should see JSON data:
   curl http://localhost:8000/api/city
   ```

2. **Is frontend serving?**
   ```bash
   # Should see HTML:
   curl http://localhost:5500
   ```

3. **Any RED errors in console?**
   - Screenshot them
   - Look for error messages

4. **Map loaded?**
   - Do you see OpenStreetMap tiles?
   - Do you see intersection dots?

---

## 💡 Quick Test

Want to test immediately? **Copy-paste this into browser console**:

```javascript
// Test if map is working
console.log('Map exists:', !!window.L);
console.log('Map initialized:', document.querySelector('#map-container'));

// Test if city data loaded
console.log('City data:', cityData ? `${cityData.intersections.length} intersections` : 'NOT LOADED');
```

---

## 🎉 Success Indicators

You'll KNOW it's working when you see:

1. **Console**: Green checkmarks (✅) in logs
2. **Map**: Bright blue line connecting start → destination
3. **Animation**: Orange circle moving along the route
4. **Chart**: SoC graph showing battery drain
5. **Metrics**: Numbers updating (time, energy, charges)

---

## 📞 Emergency Reset

If everything seems broken:

1. **Close browser completely**
2. **Restart both servers**:
   ```bash
   # Terminal 1
   uvicorn backend.app:app --reload --port 8000
   
   # Terminal 2
   cd frontend && python -m http.server 5500
   ```
3. **Open browser fresh**: `http://localhost:5500/index.html`
4. **Press F12** immediately to see console from start
5. **Click "Navigate"**
6. **Watch the console logs**

---

## ✨ You're All Set!

The route planning now has:
- ✅ Comprehensive error logging
- ✅ Helpful error messages
- ✅ Step-by-step debugging info
- ✅ Safety checks at every stage
- ✅ Clear success/failure indicators

**Your blue line WILL appear!** 🎯

Just refresh the page and check the console. You'll see exactly what's happening at every step.
