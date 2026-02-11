const BASE_URL = 'http://localhost:8000';

/**
 * Fetch the demo city graph (intersections + segments).
 * @returns {Promise<{ intersections: any[], segments: any[] }>}
 */
export async function fetchCity() {
  const res = await fetch(`${BASE_URL}/api/city`);
  if (!res.ok) {
    throw new Error(`Failed to fetch city: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch available EV vehicle presets.
 * @returns {Promise<any[]>}
 */
export async function fetchVehicles() {
  const res = await fetch(`${BASE_URL}/api/vehicles`);
  if (!res.ok) {
    throw new Error(`Failed to fetch vehicles: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Get current traffic state (intensity + blocked edges).
 * @returns {Promise<{ intensity: number, blocked_edges: { start_node_id: string, end_node_id: string }[] }>}
 */
export async function fetchTraffic() {
  const res = await fetch(`${BASE_URL}/api/traffic`);
  if (!res.ok) {
    throw new Error(`Failed to fetch traffic: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Set global traffic intensity (0–1).
 * @param {number} intensity
 * @returns {Promise<any>}
 */
export async function setTrafficIntensity(intensity) {
  const res = await fetch(`${BASE_URL}/api/traffic/intensity`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ intensity }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = data.detail || res.statusText;
    throw new Error(`Failed to set traffic: ${message}`);
  }
  return data;
}

/**
 * Block a specific directed edge (simulate accident).
 * @param {string} startNodeId
 * @param {string} endNodeId
 * @returns {Promise<any>}
 */
export async function blockEdge(startNodeId, endNodeId) {
  const res = await fetch(`${BASE_URL}/api/traffic/block`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ start_node_id: startNodeId, end_node_id: endNodeId }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = data.detail || res.statusText;
    throw new Error(`Failed to block edge: ${message}`);
  }
  return data;
}

/**
 * Plan an EV-aware route using the backend A* and cost engine.
 *
 * @param {{ startNodeId: string, endNodeId: string, vehicleId: string, mode: string, initialSoc: number }} params
 * @returns {Promise<any>}
 */
export async function planRoute({ startNodeId, endNodeId, vehicleId, mode, initialSoc }) {
  const payload = {
    start_node_id: startNodeId,
    end_node_id: endNodeId,
    vehicle_id: vehicleId,
    mode,
    initial_soc: initialSoc,
  };

  const res = await fetch(`${BASE_URL}/api/route/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data.detail || res.statusText;
    throw new Error(`Route planning failed: ${message}`);
  }

  return data;
}
