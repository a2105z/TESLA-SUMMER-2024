// Geocoding service using Nominatim (OpenStreetMap)

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';

// Autocomplete cache
let autocompleteCache = new Map();

/**
 * Geocode an address to lat/lng coordinates.
 * @param {string} address - The address to geocode
 * @returns {Promise<{lat: number, lng: number, display_name: string} | null>}
 */
export async function geocodeAddress(address) {
  if (!address || address.trim().length === 0) {
    return null;
  }

  try {
    const params = new URLSearchParams({
      q: address,
      format: 'json',
      limit: '1',
      addressdetails: '1',
    });

    const response = await fetch(`${NOMINATIM_BASE}/search?${params}`, {
      headers: {
        'User-Agent': 'TeslaNavigation/1.0',
      },
    });

    if (!response.ok) {
      throw new Error(`Geocoding failed: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.length === 0) {
      return null;
    }

    const result = data[0];
    return {
      lat: parseFloat(result.lat),
      lng: parseFloat(result.lon),
      display_name: result.display_name,
    };
  } catch (error) {
    console.error('Geocoding error:', error);
    throw new Error('Failed to geocode address. Please check your internet connection.');
  }
}

/**
 * Reverse geocode coordinates to an address.
 * @param {number} lat
 * @param {number} lng
 * @returns {Promise<string>}
 */
export async function reverseGeocode(lat, lng) {
  try {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lng.toString(),
      format: 'json',
    });

    const response = await fetch(`${NOMINATIM_BASE}/reverse?${params}`, {
      headers: {
        'User-Agent': 'TeslaNavigation/1.0',
      },
    });

    if (!response.ok) {
      return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }

    const data = await response.json();
    return data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  }
}

/**
 * Find the nearest intersection node to a given lat/lng.
 * @param {number} lat
 * @param {number} lng
 * @param {Array} intersections - Array of intersection objects with lat/lng
 * @returns {string | null} - Node ID of nearest intersection
 */
export function findNearestNode(lat, lng, intersections) {
  if (!intersections || intersections.length === 0) {
    return null;
  }

  let nearestNode = null;
  let minDistance = Infinity;

  for (const inter of intersections) {
    if (inter.lat == null || inter.lng == null) continue;

    const distance = haversineDistance(lat, lng, inter.lat, inter.lng);

    if (distance < minDistance) {
      minDistance = distance;
      nearestNode = inter.id;
    }
  }

  return nearestNode;
}

/**
 * Calculate Haversine distance between two points in km.
 */
function haversineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371; // Earth radius in km
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

/**
 * Search for address suggestions (autocomplete).
 * @param {string} query - Partial address query
 * @returns {Promise<Array<{display_name: string, lat: number, lng: number}>>}
 */
export async function searchAddresses(query) {
  if (!query || query.trim().length < 3) {
    return [];
  }

  const cacheKey = query.toLowerCase().trim();
  if (autocompleteCache.has(cacheKey)) {
    return autocompleteCache.get(cacheKey);
  }

  try {
    const params = new URLSearchParams({
      q: query,
      format: 'json',
      limit: '5',
      addressdetails: '1',
    });

    const response = await fetch(`${NOMINATIM_BASE}/search?${params}`, {
      headers: {
        'User-Agent': 'TNAV/1.0',
      },
    });

    if (!response.ok) {
      return [];
    }

    const data = await response.json();
    const results = data.map(item => ({
      display_name: item.display_name,
      lat: parseFloat(item.lat),
      lng: parseFloat(item.lon),
    }));

    autocompleteCache.set(cacheKey, results);
    return results;
  } catch (error) {
    console.error('Address search error:', error);
    return [];
  }
}
