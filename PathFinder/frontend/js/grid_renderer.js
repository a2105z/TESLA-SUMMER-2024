// City/road map renderer for TNAV using Leaflet + OpenStreetMap.
//
// Renders the CityGrid on an interactive map with:
// - Real OpenStreetMap tiles
// - Pan/zoom like Google Maps
// - Route overlay with animation
// - Intersection markers

// Check if Leaflet is loaded
if (typeof L === 'undefined') {
  console.error('Leaflet library not loaded! Make sure leaflet.js is included before this script.');
}

const mapContainer = document.getElementById('map-container');

/** @type {L.Map | null} */
let map = null;

/** @type {Map<string, L.LatLng>} */
const nodePositions = new Map();

/** @type {L.Polyline | null} */
let routePolyline = null;

/** @type {L.CircleMarker | null} */
let vehicleMarker = null;

/** @type {L.LayerGroup} */
let intersectionLayer = null;

/** @type {L.LayerGroup} */
let roadLayer = null;

/**
 * Initialize the city map using Leaflet + OpenStreetMap.
 * @param {{ intersections: any[], segments: any[] }} city
 */
export function initCityMap(city) {
  console.log('Initializing city map with city data:', city);
  
  if (!mapContainer) {
    console.error('Map container not found!');
    return;
  }
  
  // Clear existing map
  if (map) {
    console.log('Removing existing map');
    map.remove();
    map = null;
  }
  
  nodePositions.clear();
  
  const intersections = city.intersections || [];
  const segments = city.segments || [];
  
  console.log(`Loading ${intersections.length} intersections and ${segments.length} segments`);
  
  if (intersections.length === 0) {
    console.error('No intersections to display!');
    alert('Failed to load city data. Please refresh the page.');
    return;
  }
  
  // Calculate center and bounds
  const lats = intersections.filter(i => i.lat != null).map(i => i.lat);
  const lngs = intersections.filter(i => i.lng != null).map(i => i.lng);
  
  if (lats.length === 0 || lngs.length === 0) {
    console.warn('No valid coordinates');
    return;
  }
  
  const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
  const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
  
  // Initialize Leaflet map
  map = L.map('map-container', {
    center: [centerLat, centerLng],
    zoom: 15,
    zoomControl: true,
    attributionControl: true,
    preferCanvas: false,
  });
  
  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
    zIndex: 1,  // Tiles at bottom
  }).addTo(map);
  
  // Create custom pane for route overlay (ensures it's on top)
  if (!map.getPane('routePane')) {
    const routePane = map.createPane('routePane');
    routePane.style.zIndex = 650;  // Above everything (markers are 600)
    routePane.style.pointerEvents = 'none';  // Allow clicking through
  }
  
  // Create layers
  roadLayer = L.layerGroup().addTo(map);
  intersectionLayer = L.layerGroup().addTo(map);
  
  // Store node positions
  for (const inter of intersections) {
    if (inter.lat != null && inter.lng != null) {
      nodePositions.set(inter.id, L.latLng(inter.lat, inter.lng));
    } else {
      console.warn(`Intersection ${inter.id} missing coordinates`);
    }
  }
  
  console.log(`Stored ${nodePositions.size} node positions`);
  
  // Draw road segments
  for (const seg of segments) {
    const startPos = nodePositions.get(seg.start);
    const endPos = nodePositions.get(seg.end);
    
    if (!startPos || !endPos) continue;
    
    // Determine road style
    let color = '#64748b';  // local
    let weight = 3;
    let opacity = 0.6;
    
    if (seg.road_class === 'arterial') {
      color = '#94a3b8';
      weight = 4;
      opacity = 0.7;
    } else if (seg.road_class === 'highway') {
      color = '#cbd5e1';
      weight = 5;
      opacity = 0.8;
    }
    
    const line = L.polyline([startPos, endPos], {
      color: color,
      weight: weight,
      opacity: opacity,
      interactive: false,
    });
    
    roadLayer.addLayer(line);
  }
  
  // Draw intersection nodes
  for (const inter of intersections) {
    const pos = nodePositions.get(inter.id);
    if (!pos) continue;
    
    // Style based on charger availability
    const marker = L.circleMarker(pos, {
      radius: inter.has_charger ? 5 : 3,
      fillColor: inter.has_charger ? '#4ade80' : '#3b82f6',
      fillOpacity: inter.has_charger ? 0.9 : 0.7,
      color: inter.has_charger ? '#22c55e' : '#2563eb',
      weight: inter.has_charger ? 2 : 1,
      interactive: true,
    });
    
    // Add tooltip
    marker.bindTooltip(inter.name || inter.id, {
      permanent: false,
      direction: 'top',
      className: 'intersection-tooltip',
    });
    
    intersectionLayer.addLayer(marker);
  }
  
  // Fit map to show all intersections
  const bounds = L.latLngBounds(intersections.map(i => [i.lat, i.lng]));
  map.fitBounds(bounds, { padding: [50, 50] });
  
  console.log('✅ Map initialization complete!');
  console.log(`Map center: ${map.getCenter()}, Zoom: ${map.getZoom()}`);
}

/**
 * Highlight the planned route and return its lat/lng points.
 * @param {string[]} nodeIds
 * @returns {L.LatLng[]} ordered lat/lng points along the route
 */
export function drawRoute(nodeIds) {
  console.log('drawRoute called with:', nodeIds);
  
  if (!map) {
    console.error('Map not initialized!');
    return [];
  }
  
  if (!nodeIds || nodeIds.length === 0) {
    console.warn('No node IDs provided to drawRoute');
    return [];
  }
  
  // Remove existing route
  if (routePolyline) {
    console.log('Removing old route');
    map.removeLayer(routePolyline);
    routePolyline = null;
  }
  
  // Convert node IDs to lat/lng points
  const points = [];
  const missingNodes = [];
  
  for (const id of nodeIds) {
    const pos = nodePositions.get(id);
    if (pos) {
      points.push(pos);
    } else {
      missingNodes.push(id);
    }
  }
  
  if (missingNodes.length > 0) {
    console.warn('Missing positions for nodes:', missingNodes);
    console.log('Available nodes:', Array.from(nodePositions.keys()));
  }
  
  if (points.length === 0) {
    console.error('No valid points found! Cannot draw route.');
    alert('Route planning failed: Could not find node positions on map. Please refresh the page and try again.');
    return [];
  }
  
  console.log(`Drawing route with ${points.length} points`);
  
  // Draw route with bright Tesla blue line!
  routePolyline = L.polyline(points, {
    color: '#00d4ff',       // BRIGHT cyan blue (Tesla style)
    weight: 6,              // Visible but elegant
    opacity: 1.0,           // Fully solid
    lineJoin: 'round',
    lineCap: 'round',
    interactive: false,
    smoothFactor: 0.5,
    pane: 'routePane',      // Use custom pane (z-index 650)
  });
  
  // Add glow effect with a shadow polyline underneath
  const shadowPolyline = L.polyline(points, {
    color: '#00d4ff',       // Matching blue shadow
    weight: 12,
    opacity: 0.3,
    lineJoin: 'round',
    lineCap: 'round',
    interactive: false,
    pane: 'routePane',
  });
  
  shadowPolyline.addTo(map);
  routePolyline.addTo(map);
  
  console.log('✅ Route polyline added to map with GLOW effect!');
  console.log('✅ Route is in custom pane with z-index 650 (ON TOP OF EVERYTHING)');
  console.log('Polyline bounds:', routePolyline.getBounds());
  
  // Force a map update to ensure it renders
  map.invalidateSize();
  setTimeout(() => map.invalidateSize(), 100);
  
  // Fit map to route
  if (points.length > 1) {
    const bounds = routePolyline.getBounds();
    map.fitBounds(bounds, { padding: [80, 80] });
    console.log('Map fitted to route bounds');
  }
  
  return points;
}

/**
 * Ensure vehicle marker exists.
 */
export function ensureVehicleIcon() {
  if (!map) return;
  
  if (!vehicleMarker) {
    vehicleMarker = L.circleMarker([0, 0], {
      radius: 8,
      fillColor: '#f59e0b',
      fillOpacity: 1.0,
      color: '#ffffff',
      weight: 2,
      interactive: false,
      zIndexOffset: 1000,
    });
    vehicleMarker.addTo(map);
  }
}

/**
 * Update vehicle marker position.
 * @param {L.LatLng} latLng
 */
export function setVehiclePosition(latLng) {
  if (!vehicleMarker || !map) return;
  vehicleMarker.setLatLng(latLng);
}

// Export map instance for external access
export function getMap() {
  return map;
}
