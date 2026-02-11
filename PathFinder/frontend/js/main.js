import { initCityMap, drawRoute, getMap } from './grid_renderer.js';
import { animateRoute } from './route_animator.js';
import { initSocChart, updateSocChart } from './soc_chart.js';
import { geocodeAddress, findNearestNode } from './geocoding.js';
import { setupAutocomplete } from './autocomplete.js';
import { fetchCity, fetchVehicles, planRoute, setTrafficIntensity } from './api.js';

// DOM elements
const vehicleSelect = document.getElementById('vehicle-select');
const startAddressInput = document.getElementById('start-address');
const endAddressInput = document.getElementById('end-address');
const planRouteBtn = document.getElementById('plan-route-btn');
const modeToggle = document.getElementById('mode-toggle');
const initialSocSlider = document.getElementById('initial-soc');
const initialSocLabel = document.getElementById('initial-soc-label');
const trafficIntensitySlider = document.getElementById('traffic-intensity');
const trafficIntensityLabel = document.getElementById('traffic-intensity-label');
const metricTime = document.getElementById('metric-time');
const metricEnergy = document.getElementById('metric-energy');
const metricCharges = document.getElementById('metric-charges');
const metricCurrentSoc = document.getElementById('metric-current-soc');
const routeStepsList = document.getElementById('route-steps');
const socCanvas = document.getElementById('soc-chart');

let currentMode = 'balanced';
let cityData = null;
let vehicles = [];
let lastRequestParams = null;
let lastRouteSteps = null;

function setLoadingState(isLoading) {
  planRouteBtn.disabled = isLoading;
  planRouteBtn.textContent = isLoading ? 'Planning...' : 'Plan Route';
}

function updateInitialSocLabel() {
  if (!initialSocSlider || !initialSocLabel) return;
  initialSocLabel.textContent = `${initialSocSlider.value}%`;
}

function updateTrafficIntensityLabel() {
  if (!trafficIntensitySlider || !trafficIntensityLabel) return;
  const value = Number(trafficIntensitySlider.value);
  let label = 'Low';
  if (value <= 5) label = 'Free';
  else if (value < 35) label = 'Low';
  else if (value < 70) label = 'Medium';
  else if (value < 90) label = 'High';
  else label = 'Severe';
  trafficIntensityLabel.textContent = label;
}

function onModeButtonClick(e) {
  const btn = e.target.closest('.mode-btn');
  if (!btn) return;
  const mode = btn.getAttribute('data-mode');
  if (!mode) return;
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach((b) => {
    b.classList.toggle('mode-btn-active', b === btn);
  });
}

function setDefaultAddresses() {
  // Default to Chicago Loop demo addresses
  startAddressInput.value = 'Millennium Park, Chicago, IL';
  endAddressInput.value = 'Willis Tower, Chicago, IL';
  console.log('Default addresses set:', {
    start: startAddressInput.value,
    end: endAddressInput.value
  });
}

function populateVehicleSelect(vehiclesList) {
  vehicleSelect.innerHTML = '';
  for (const v of vehiclesList) {
    const opt = document.createElement('option');
    opt.value = v.id;
    opt.textContent = v.name;
    vehicleSelect.appendChild(opt);
  }
}

function computeDistanceProfileFromSteps(steps) {
  if (!cityData || !steps || steps.length === 0) return [];
  const segs = cityData.segments || [];
  const distanceMap = new Map();
  for (const seg of segs) {
    distanceMap.set(`${seg.start}-${seg.end}`, seg.distance_km);
  }
  let cumulative = 0;
  const profile = [];
  profile.push({ distance_km: 0, soc: steps[0].soc * 100 });
  for (let i = 1; i < steps.length; i++) {
    const prev = steps[i - 1];
    const cur = steps[i];
    const key = `${prev.node_id}-${cur.node_id}`;
    const dist = distanceMap.get(key) || 0;
    cumulative += dist;
    profile.push({ distance_km: cumulative, soc: cur.soc * 100 });
  }
  return profile;
}

function renderRouteSteps(steps) {
  routeStepsList.innerHTML = '';
  if (!steps || steps.length === 0) return;
  steps.forEach((step, idx) => {
    const li = document.createElement('li');
    if (step.is_charging_stop) {
      li.classList.add('charging-step');
    }
    const nodeSpan = document.createElement('span');
    nodeSpan.className = 'step-node';
    nodeSpan.textContent = `${idx + 1}. ${step.node_id}`;

    const socSpan = document.createElement('span');
    socSpan.className = 'step-soc';
    socSpan.textContent = `${Math.round(step.soc * 100)}%`;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'step-time';
    timeSpan.textContent = `${step.cumulative_time_hours.toFixed(2)}h`;

    li.appendChild(nodeSpan);
    li.appendChild(socSpan);
    li.appendChild(timeSpan);
    routeStepsList.appendChild(li);
  });
}

async function initialize() {
  try {
    console.log('🚀 Initializing TNAV...');
    
    if (socCanvas) {
      initSocChart(socCanvas);
      console.log('✅ SoC chart initialized');
    }

    console.log('📡 Fetching city data and vehicles from backend...');
    console.log('Backend URL: http://localhost:8000');
    
    const [city, vehiclesResponse] = await Promise.all([
      fetchCity().then(data => {
        console.log('✅ City data received:', data);
        return data;
      }).catch(err => {
        console.error('❌ Failed to fetch city:', err);
        throw new Error(`City data fetch failed: ${err.message}`);
      }),
      fetchVehicles().then(data => {
        console.log('✅ Vehicles data received:', data);
        return data;
      }).catch(err => {
        console.error('❌ Failed to fetch vehicles:', err);
        throw new Error(`Vehicles fetch failed: ${err.message}`);
      }),
    ]);
    
    cityData = city;
    vehicles = vehiclesResponse;

    console.log('🗺️ Initializing city map...');
    initCityMap(cityData);
    console.log('✅ Map initialized');
    
    setDefaultAddresses();
    populateVehicleSelect(vehicles);

    // Setup address autocomplete
    setupAutocomplete(startAddressInput, (result) => {
      console.log('Start address selected:', result.display_name);
    });
    setupAutocomplete(endAddressInput, (result) => {
      console.log('End address selected:', result.display_name);
    });

    updateInitialSocLabel();
    updateTrafficIntensityLabel();
    
    console.log('✅ TNAV initialized successfully!');
    console.log('City data loaded:', cityData.intersections.length, 'intersections');
    console.log('Vehicles loaded:', vehicles.length, 'models');
    
    // Add test function to window for debugging
    window.testRoute = testDrawRoute;
    
    // Auto-plan a demo route on load to show the system in action
    setTimeout(() => {
      console.log('Auto-planning demo route...');
      if (startAddressInput.value && endAddressInput.value) {
        handlePlanRoute();
      } else {
        console.warn('No default addresses set');
      }
    }, 1000);
  } catch (err) {
    console.error('❌ INITIALIZATION FAILED:', err);
    console.error('Error details:', err.message);
    console.error('Stack trace:', err.stack);
    alert(`Failed to initialize TNAV!\n\nError: ${err.message}\n\nMake sure:\n1. Backend is running on http://localhost:8000\n2. You have internet access for OpenStreetMap tiles\n3. Check browser console for details`);
  }
}

async function handlePlanRoute() {
  if (!cityData || !vehicles.length) {
    console.error('City data or vehicles not loaded');
    return;
  }

  const startAddress = startAddressInput.value.trim();
  const endAddress = endAddressInput.value.trim();
  const vehicleId = vehicleSelect.value;
  const initialSoc = Number(initialSocSlider.value) / 100;

  if (!startAddress || !endAddress || !vehicleId) {
    alert('Please enter starting address, destination, and select a Tesla model.');
    return;
  }

  console.log('Planning route:', { startAddress, endAddress, vehicleId, mode: currentMode, initialSoc });
  setLoadingState(true);

  try {
    // Geocode both addresses
    console.log('Geocoding addresses...');
    const [startGeo, endGeo] = await Promise.all([
      geocodeAddress(startAddress),
      geocodeAddress(endAddress),
    ]);

    console.log('Geocoded:', { start: startGeo, end: endGeo });

    if (!startGeo) {
      alert(`Could not find: "${startAddress}". Please try a different address.`);
      setLoadingState(false);
      return;
    }

    if (!endGeo) {
      alert(`Could not find: "${endAddress}". Please try a different address.`);
      setLoadingState(false);
      return;
    }

    // Find nearest nodes in the network
    console.log('Finding nearest nodes...');
    const startNode = findNearestNode(startGeo.lat, startGeo.lng, cityData.intersections);
    const endNode = findNearestNode(endGeo.lat, endGeo.lng, cityData.intersections);

    console.log('Nearest nodes:', { startNode, endNode });

    if (!startNode || !endNode) {
      alert('Addresses are outside the demo network. Please choose locations in downtown Chicago.');
      setLoadingState(false);
      return;
    }

    // Pan map to show route area
    const map = getMap();
    if (map) {
      console.log('Panning map to show route area');
      map.fitBounds([
        [startGeo.lat, startGeo.lng],
        [endGeo.lat, endGeo.lng]
      ], { padding: [100, 100] });
    }

    const params = {
      startNodeId: startNode,
      endNodeId: endNode,
      vehicleId,
      mode: currentMode,
      initialSoc,
    };
    lastRequestParams = params;
    console.log('Calling backend with params:', params);
    await runPlanRoute(params);
  } catch (error) {
    console.error('Route planning error:', error);
    alert(error.message || 'Failed to plan route. Please check your internet connection.');
    setLoadingState(false);
  }
}

async function runPlanRoute(params) {
  setLoadingState(true);

  try {
    console.log('Calling planRoute API...');
    const result = await planRoute(params);
    console.log('Route result:', result);

    const steps = result.steps || [];
    console.log('Route steps:', steps.length);
    lastRouteSteps = steps;
    const nodeIds = steps.map((s) => s.node_id);
    console.log('Node IDs:', nodeIds);

    console.log('Drawing route...');
    const points = drawRoute(nodeIds);
    console.log('Route points:', points.length);

    const profile = computeDistanceProfileFromSteps(steps);
    updateSocChart(profile);
    renderRouteSteps(steps);

    metricTime.textContent = `${result.total_time_hours.toFixed(2)} h`;
    metricEnergy.textContent = `${result.total_energy_kwh.toFixed(2)} kWh`;
    metricCharges.textContent = String(result.charging_stops?.length || 0);
    metricCurrentSoc.textContent = steps.length
      ? `${Math.round(steps[steps.length - 1].soc * 100)}%`
      : '–';

    console.log('Starting animation...');
    animateRoute(points, steps, (soc) => {
      metricCurrentSoc.textContent = `${Math.round(soc * 100)}%`;
    });
  } catch (err) {
    console.error('Run plan route error:', err);
    alert(err.message || 'Failed to plan route.');
  } finally {
    setLoadingState(false);
  }
}

// Test Route Button - Uses hardcoded node IDs for demo
async function handleTestRoute() {
  console.log('🧪 Running test route with hardcoded nodes...');
  
  if (!cityData || !vehicles.length) {
    alert('City data not loaded yet. Please wait and try again.');
    return;
  }
  
  const vehicleId = vehicleSelect.value || vehicles[0]?.id;
  const initialSoc = Number(initialSocSlider.value) / 100;
  
  // Hardcoded route: Diagonal across the entire Chicago Loop
  const params = {
    startNodeId: 'wacker_michigan',     // North-East: Wacker & Michigan
    endNodeId: 'vanburen_wells',        // South-West: Van Buren & Wells
    vehicleId,
    mode: currentMode,
    initialSoc,
  };
  
  console.log('Test route params:', params);
  console.log('This should show a LONG diagonal route across the entire Chicago Loop!');
  
  await runPlanRoute(params);
}

// Event wiring
if (modeToggle) {
  modeToggle.addEventListener('click', onModeButtonClick);
}
if (initialSocSlider) {
  initialSocSlider.addEventListener('input', updateInitialSocLabel);
}
if (planRouteBtn) {
  planRouteBtn.addEventListener('click', handlePlanRoute);
}

const testRouteBtn = document.getElementById('test-route-btn');
if (testRouteBtn) {
  testRouteBtn.addEventListener('click', handleTestRoute);
}

if (trafficIntensitySlider) {
  trafficIntensitySlider.addEventListener('input', () => {
    updateTrafficIntensityLabel();
  });
  trafficIntensitySlider.addEventListener('change', async () => {
    const value = Number(trafficIntensitySlider.value) / 100;
    try {
      await setTrafficIntensity(value);
      // Re-plan with new traffic if we already have a prior request
      if (lastRequestParams) {
        await runPlanRoute(lastRequestParams);
      }
    } catch (err) {
      console.error(err);
      alert(err.message || 'Failed to update traffic intensity.');
    }
  });
}

// Accident simulation removed - Tesla Navigation focuses on optimal routing

// Test function to verify route drawing works
function testDrawRoute() {
  console.log('🧪 Testing route drawing...');
  if (!cityData) {
    console.error('City data not loaded yet');
    return;
  }
  
  // Draw a simple route down Michigan Avenue
  const testNodes = [
    'wacker_michigan',
    'lake_michigan',
    'randolph_michigan',
    'washington_michigan',
    'madison_michigan',
    'monroe_michigan',
    'adams_michigan',
    'jackson_michigan',
    'vanburen_michigan'
  ];
  
  console.log('Drawing test route with nodes:', testNodes);
  const points = drawRoute(testNodes);
  console.log('Test route drew:', points.length, 'points');
  
  if (points.length > 0) {
    console.log('✅ SUCCESS! Route drawing works! You should see a blue line down Michigan Ave.');
  } else {
    console.error('❌ FAILED! Route drawing did not work.');
  }
}

// Make test function available in console
window.testRoute = testDrawRoute;

// Diagnostic function to check map layers
window.checkMapLayers = function() {
  console.log('🔍 Checking map layers...');
  const panes = ['tilePane', 'overlayPane', 'markerPane', 'routePane'];
  panes.forEach(paneName => {
    const pane = map.getPane(paneName);
    if (pane) {
      console.log(`✅ ${paneName}: z-index = ${pane.style.zIndex || 'default'}`);
    } else {
      console.log(`❌ ${paneName}: NOT FOUND`);
    }
  });
  
  if (routePolyline) {
    console.log('✅ Route polyline exists:', routePolyline);
    console.log('   Bounds:', routePolyline.getBounds());
    console.log('   Is added to map:', map.hasLayer(routePolyline));
  } else {
    console.log('❌ No route polyline found');
  }
};

// Kick off initialization
initialize();