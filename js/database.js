/* TinyFit Jewelry — Brand Database Filter/Sort */
(function () {
  let brands = [];
  const grid = document.getElementById('brand-grid');
  const countEl = document.getElementById('result-count');

  const catFilter = document.getElementById('filter-category');
  const sizeFilter = document.getElementById('filter-size');
  const priceFilter = document.getElementById('filter-price');
  const matFilter = document.getElementById('filter-material');
  const adjFilter = document.getElementById('filter-adjustable');
  const sortSelect = document.getElementById('sort-by');
  const searchInput = document.getElementById('search-brand');

  async function loadData() {
    const res = await fetch('data/brands.json');
    brands = await res.json();
    render();
  }

  function getFiltered() {
    let filtered = [...brands];
    const cat = catFilter.value;
    const maxSize = parseFloat(sizeFilter.value) || 99;
    const maxPrice = parseInt(priceFilter.value) || 999999;
    const mat = matFilter.value.toLowerCase();
    const adj = adjFilter.value;
    const q = searchInput.value.toLowerCase().trim();

    if (cat) filtered = filtered.filter(b => b.category.includes(cat));
    if (sizeFilter.value) {
      filtered = filtered.filter(b => {
        if (cat === 'bracelet') return b.min_bracelet_cm !== null && b.min_bracelet_cm <= maxSize;
        return b.min_ring_size_us !== null && b.min_ring_size_us <= maxSize;
      });
    }
    if (priceFilter.value) filtered = filtered.filter(b => b.price_min <= maxPrice);
    if (mat) filtered = filtered.filter(b => b.materials.some(m => m.toLowerCase().includes(mat)));
    if (adj === 'yes') filtered = filtered.filter(b => b.adjustable);
    if (adj === 'no') filtered = filtered.filter(b => !b.adjustable);
    if (q) filtered = filtered.filter(b => b.brand.toLowerCase().includes(q) || b.country.toLowerCase().includes(q) || b.note.toLowerCase().includes(q));

    const sort = sortSelect.value;
    if (sort === 'size-asc') filtered.sort((a, b) => (a.min_ring_size_us || 99) - (b.min_ring_size_us || 99));
    else if (sort === 'price-asc') filtered.sort((a, b) => a.price_min - b.price_min);
    else if (sort === 'price-desc') filtered.sort((a, b) => b.price_max - a.price_max);
    else if (sort === 'name') filtered.sort((a, b) => a.brand.localeCompare(b.brand));

    return filtered;
  }

  function countryFlag(c) {
    const flags = { 'Japan': 'JP', 'USA': 'US', 'Canada': 'CA', 'UK': 'UK', 'France': 'FR', 'Kenya/USA': 'KE', 'Japan/USA': 'JP/US', 'China': 'CN', 'International': 'INT' };
    return flags[c] || c;
  }

  function renderCard(b) {
    const cats = b.category.map(c => '<span class="tag">' + c + '</span>').join('');
    const mats = b.materials.slice(0, 3).map(m => '<span class="tag tag-gold">' + m + '</span>').join('');
    const sizeInfo = [];
    if (b.min_ring_size_us !== null) sizeInfo.push('Ring from US ' + b.min_ring_size_us);
    if (b.min_bracelet_cm !== null) sizeInfo.push('Bracelet from ' + b.min_bracelet_cm + 'cm');
    const sizeStr = sizeInfo.length ? sizeInfo.map(s => '<span class="tag tag-green">' + s + '</span>').join('') : '';
    const adjBadge = b.adjustable ? '<span class="tag tag-green">Adjustable</span>' : '';

    return '<div class="brand-card">' +
      '<h3>' + b.brand + ' <span class="country-flag">' + countryFlag(b.country) + '</span></h3>' +
      '<div class="brand-meta">' + cats + sizeStr + adjBadge + '</div>' +
      '<div class="brand-meta">' + mats + '</div>' +
      '<div class="price">$' + b.price_min + ' &ndash; $' + b.price_max + '</div>' +
      '<p class="note">' + b.note + '</p>' +
      '<a href="' + (b.affiliate_url || b.shop_url) + '" target="_blank" rel="noopener noreferrer" class="shop-btn">Visit Brand</a>' +
      (b.amazon_url ? '<a href="' + b.amazon_url + '" target="_blank" rel="noopener noreferrer" class="shop-btn" style="margin-left:6px;background:#FF9900;color:#111;">Amazon</a>' : '') +
      '</div>';
  }

  function render() {
    const filtered = getFiltered();
    countEl.textContent = filtered.length + ' brand' + (filtered.length !== 1 ? 's' : '') + ' found';
    if (filtered.length === 0) {
      grid.innerHTML = '<div class="no-results"><p>No brands match your filters. Try adjusting your criteria.</p></div>';
      return;
    }
    grid.innerHTML = filtered.map(renderCard).join('');
  }

  [catFilter, sizeFilter, priceFilter, matFilter, adjFilter, sortSelect].forEach(el => el.addEventListener('change', render));
  searchInput.addEventListener('input', render);

  loadData();
})();
