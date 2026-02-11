/**
 * Simple SoC line chart using Canvas.
 *
 * X-axis: cumulative distance (km)
 * Y-axis: state of charge (0–100%)
 */

/** @type {HTMLCanvasElement | null} */
let canvas = null;
/** @type {CanvasRenderingContext2D | null} */
let ctx = null;

export function initSocChart(canvasEl) {
  canvas = canvasEl;
  if (!canvas) return;
  ctx = canvas.getContext('2d');
}

/**
 * @param {{ distance_km: number, soc: number }[]} profile
 */
export function updateSocChart(profile) {
  if (!canvas || !ctx) return;
  const width = canvas.width = canvas.clientWidth * window.devicePixelRatio;
  const height = canvas.height = canvas.clientHeight * window.devicePixelRatio;

  ctx.clearRect(0, 0, width, height);

  if (!profile || profile.length === 0) {
    return;
  }

  const minX = 0;
  const maxX = Math.max(...profile.map(p => p.distance_km));
  const minY = 0;
  const maxY = 100;

  const padX = 40 * window.devicePixelRatio;
  const padY = 20 * window.devicePixelRatio;

  function xScale(d) {
    if (maxX === minX) return padX;
    return padX + ((d - minX) / (maxX - minX)) * (width - padX * 1.5);
  }

  function yScale(soc) {
    return height - padY - ((soc - minY) / (maxY - minY)) * (height - padY * 2);
  }

  // Axes
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.6)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  // Y axis
  ctx.moveTo(padX, padY);
  ctx.lineTo(padX, height - padY);
  // X axis
  ctx.lineTo(width - padX * 0.5, height - padY);
  ctx.stroke();

  ctx.fillStyle = 'rgba(148, 163, 184, 0.9)';
  ctx.font = `${12 * window.devicePixelRatio}px Arial`;
  ctx.fillText('SoC %', padX - 30 * window.devicePixelRatio, padY - 5 * window.devicePixelRatio);
  ctx.fillText('Distance (km)', width - 130 * window.devicePixelRatio, height - 4 * window.devicePixelRatio);

  // SoC line
  ctx.beginPath();
  profile.forEach((p, i) => {
    const x = xScale(p.distance_km);
    const y = yScale(p.soc);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  const grad = ctx.createLinearGradient(padX, 0, width - padX, 0);
  grad.addColorStop(0, '#38bdf8');
  grad.addColorStop(1, '#22c55e');
  ctx.strokeStyle = grad;
  ctx.lineWidth = 2 * window.devicePixelRatio;
  ctx.stroke();

  // Fill under curve
  ctx.lineTo(xScale(profile[profile.length - 1].distance_km), yScale(0));
  ctx.lineTo(xScale(profile[0].distance_km), yScale(0));
  ctx.closePath();
  ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
  ctx.fill();
}

