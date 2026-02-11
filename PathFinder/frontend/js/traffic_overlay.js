/**
 * Traffic overlay for EVNav.
 *
 * For the demo we simply color roads by global traffic intensity:
 * - Green: light
 * - Yellow: medium
 * - Red: heavy
 */

export function initTrafficOverlay() {
  // Nothing to initialize yet; the roads are part of the main SVG.
}

/**
 * @param {{ intensity: number }} opts
 */
export function updateTrafficOverlay(opts) {
  const intensity = Math.max(0, Math.min(1, opts?.intensity ?? 0));
  const roads = document.querySelectorAll('.map-road');
  let color;
  if (intensity < 0.25) {
    color = '#22c55e'; // green
  } else if (intensity < 0.6) {
    color = '#eab308'; // yellow
  } else {
    color = '#ef4444'; // red
  }

  roads.forEach((el) => {
    const elem = /** @type {SVGElement} */ (el);
    elem.style.stroke = color;
    elem.style.opacity = String(0.7 + 0.3 * intensity);
  });
}

