// Address autocomplete for search bars (Google Maps style)

import { searchAddresses } from './geocoding.js';

let debounceTimer = null;

/**
 * Setup autocomplete for an input element.
 * @param {HTMLInputElement} input
 * @param {Function} onSelect - Callback when address is selected
 */
export function setupAutocomplete(input, onSelect) {
  if (!input) return;

  const wrapper = input.parentElement;
  let dropdown = wrapper.querySelector('.autocomplete-dropdown');

  // Create dropdown if doesn't exist
  if (!dropdown) {
    dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown';
    dropdown.style.display = 'none';
    wrapper.appendChild(dropdown);
  }

  // Handle input changes
  input.addEventListener('input', async (e) => {
    const query = e.target.value.trim();

    // Clear previous timer
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    if (query.length < 3) {
      dropdown.style.display = 'none';
      return;
    }

    // Debounce API calls (wait 300ms after user stops typing)
    debounceTimer = setTimeout(async () => {
      try {
        const results = await searchAddresses(query);

        if (results.length === 0) {
          dropdown.style.display = 'none';
          return;
        }

        // Populate dropdown
        dropdown.innerHTML = '';
        results.forEach((result) => {
          const item = document.createElement('div');
          item.className = 'autocomplete-item';
          item.textContent = result.display_name;

          item.addEventListener('click', () => {
            input.value = result.display_name;
            dropdown.style.display = 'none';
            if (onSelect) {
              onSelect(result);
            }
          });

          dropdown.appendChild(item);
        });

        dropdown.style.display = 'block';
      } catch (error) {
        console.error('Autocomplete error:', error);
        dropdown.style.display = 'none';
      }
    }, 300);
  });

  // Hide dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });

  // Hide on Enter key
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      dropdown.style.display = 'none';
    }
  });
}
