// Route animation for EVNav.
//
// Animates a small "vehicle" icon along the planned route polyline
// and provides hooks to update the UI with the current SoC.

import { ensureVehicleIcon, setVehiclePosition } from './grid_renderer.js';

/**
 * Animate the vehicle along the given polyline.
 *
 * @param {L.LatLng[]} points - Array of Leaflet LatLng points
 * @param {{ node_id: string, soc: number, cumulative_time_hours: number, cumulative_energy_kwh: number, is_charging_stop: boolean }[]} steps
 * @param {(soc: number) => void} onSocUpdate
 */
export function animateRoute(points, steps, onSocUpdate) {
  if (!points || points.length < 2 || !steps || steps.length === 0) {
    return;
  }

  ensureVehicleIcon();

  // Map each polyline point to its corresponding step index
  const stepCount = steps.length;
  const totalSegments = points.length - 1;

  const durationMs = 4000; // total animation duration in ms
  const startTime = performance.now();

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function getInterpolatedSoc(tNorm) {
    // tNorm in [0,1]; map to steps
    const idxFloat = tNorm * (stepCount - 1);
    const i = Math.floor(idxFloat);
    const frac = idxFloat - i;
    const s0 = steps[i];
    const s1 = steps[Math.min(i + 1, stepCount - 1)];
    return lerp(s0.soc, s1.soc, frac);
  }

  function frame(now) {
    const elapsed = now - startTime;
    let t = elapsed / durationMs;
    if (t > 1) t = 1;

    const segmentFloat = t * totalSegments;
    const segIdx = Math.min(Math.floor(segmentFloat), totalSegments - 1);
    const segT = segmentFloat - segIdx;

    const p0 = points[segIdx];
    const p1 = points[Math.min(segIdx + 1, points.length - 1)]; // Prevent out of bounds
    
    // Safety check
    if (!p0 || !p1) {
      console.error('Invalid animation points:', {segIdx, p0, p1, pointsLength: points.length});
      return;
    }
    
    // Interpolate lat/lng for Leaflet
    const latLng = L.latLng(
      lerp(p0.lat, p1.lat, segT),
      lerp(p0.lng, p1.lng, segT)
    );

    setVehiclePosition(latLng);

    const soc = getInterpolatedSoc(t);
    if (typeof onSocUpdate === 'function') {
      onSocUpdate(soc);
    }

    if (t < 1) {
      requestAnimationFrame(frame);
    }
  }

  requestAnimationFrame(frame);
}
