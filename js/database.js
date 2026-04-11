/* TinyFit Jewelry — Brand Database Filter/Sort + Wishlist */
(function () {
  let brands = [];
  const grid = document.getElementById('brand-grid');
  const communityGrid = document.getElementById('community-grid');
  const communitySection = document.getElementById('community-section');
  const countEl = document.getElementById('result-count');

  const catFilter = document.getElementById('filter-category');
  const sizeFilter = document.getElementById('filter-size');
  const priceFilter = document.getElementById('filter-price');
  const matFilter = document.getElementById('filter-material');
  const adjFilter = document.getElementById('filter-adjustable');
  const shipFilter = document.getElementById('filter-shipping');
  const sortSelect = document.getElementById('sort-by');
  const searchInput = document.getElementById('search-brand');

  // Wishlist (localStorage)
  function getWishlist() {
    try { return JSON.parse(localStorage.getItem('tinyfit_wishlist') || '[]'); } catch { return []; }
  }
  function toggleWishlist(brandName) {
    let wl = getWishlist();
    if (wl.includes(brandName)) wl = wl.filter(n => n !== brandName);
    else wl.push(brandName);
    localStorage.setItem('tinyfit_wishlist', JSON.stringify(wl));
    render();
    updateWishlistCount();
  }
  function updateWishlistCount() {
    const el = document.getElementById('wishlist-count');
    if (el) { const c = getWishlist().length; el.textContent = c > 0 ? c : ''; el.style.display = c > 0 ? 'inline-flex' : 'none'; }
  }
  // Expose toggle globally for onclick
  window.toggleWishlist = toggleWishlist;

  async function loadData() {
    const res = await fetch('data/brands.json');
    brands = await res.json();
    render();
    updateWishlistCount();
  }

  function getFiltered() {
    let filtered = [...brands];
    const cat = catFilter.value;
    const maxSize = parseFloat(sizeFilter.value) || 99;
    const maxPrice = parseInt(priceFilter.value) || 999999;
    const mat = matFilter.value.toLowerCase();
    const adj = adjFilter.value;
    const q = searchInput.value.toLowerCase().trim();

    if (cat === 'wishlist') {
      const wl = getWishlist();
      filtered = filtered.filter(b => wl.includes(b.brand));
    } else {
      if (cat) filtered = filtered.filter(b => b.category.includes(cat));
    }
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
    const ship = shipFilter ? shipFilter.value : '';
    if (ship === 'intl') filtered = filtered.filter(b => b.intl_shipping !== false);
    if (ship === 'japan') filtered = filtered.filter(b => b.intl_shipping === false);
    if (q) filtered = filtered.filter(b => b.brand.toLowerCase().includes(q) || b.country.toLowerCase().includes(q) || b.note.toLowerCase().includes(q));

    const sort = sortSelect.value;
    if (sort === 'intl-first') filtered.sort((a, b) => {
      const aIntl = a.intl_shipping !== false ? 0 : 1;
      const bIntl = b.intl_shipping !== false ? 0 : 1;
      if (aIntl !== bIntl) return aIntl - bIntl;
      return (a.min_ring_size_us || 99) - (b.min_ring_size_us || 99);
    });
    else if (sort === 'size-asc') filtered.sort((a, b) => (a.min_ring_size_us || 99) - (b.min_ring_size_us || 99));
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
    const japanBadge = b.intl_shipping === false ? '<span class="tag tag-japan">Japan Only</span>' : '';
    const isSaved = getWishlist().includes(b.brand);
    const heartBtn = '<button onclick="toggleWishlist(\'' + b.brand.replace(/'/g, "\\'") + '\')" style="position:absolute;top:12px;right:12px;background:none;border:none;font-size:1.3rem;cursor:pointer;padding:4px;" title="' + (isSaved ? 'Remove from saved' : 'Save brand') + '">' + (isSaved ? '&#10084;&#65039;' : '&#9825;') + '</button>';

    return '<div class="brand-card" style="position:relative;">' + heartBtn +
      '<h3>' + b.brand + ' <span class="country-flag">' + countryFlag(b.country) + '</span>' + japanBadge + '</h3>' +
      '<div class="brand-meta">' + cats + sizeStr + adjBadge + '</div>' +
      '<div class="brand-meta">' + mats + '</div>' +
      '<div class="price">$' + b.price_min + ' &ndash; $' + b.price_max + '</div>' +
      '<p class="note">' + b.note + '</p>' +
      (b.verified_date ? '<p style="font-size:0.7rem;color:var(--muted);margin-top:2px;">Verified ' + b.verified_date + '</p>' : '') +
      '<a href="' + (b.affiliate_url || b.shop_url) + '" target="_blank" rel="noopener noreferrer" class="shop-btn">' + (b.intl_shipping === false ? 'View (Japan Only)' : 'Visit Brand') + '</a>' +
      (b.affiliate_url ? '<span style="font-size:0.7rem;color:var(--muted);margin-top:2px;">affiliate link</span>' : '') +
      (b.amazon_url ? '<a href="' + b.amazon_url + '" target="_blank" rel="noopener noreferrer" class="shop-btn" style="margin-left:6px;background:#FF9900;color:#111;">Amazon</a>' : '') +
      '</div>';
  }

  function render() {
    const filtered = getFiltered();
    const mainBrands = filtered.filter(b => !b.is_community_pick);
    const communityPicks = filtered.filter(b => b.is_community_pick);

    const mainCount = mainBrands.length;
    const commCount = communityPicks.length;
    let countText = mainCount + ' brand' + (mainCount !== 1 ? 's' : '') + ' found';
    if (commCount > 0) countText += ' + ' + commCount + ' community pick' + (commCount !== 1 ? 's' : '');
    countEl.textContent = countText;

    if (mainCount === 0) {
      const isWishlist = catFilter.value === 'wishlist';
      grid.innerHTML = '<div class="no-results"><p>' + (isWishlist ? 'No saved brands yet. Click the heart icon on any brand to save it here.' : 'No brands match your filters. Try adjusting your criteria.') + '</p></div>';
    } else {
      grid.innerHTML = mainBrands.map(renderCard).join('');
    }

    if (communityGrid && communitySection) {
      if (commCount > 0) {
        communityGrid.innerHTML = communityPicks.map(renderCard).join('');
        communitySection.style.display = 'block';
      } else {
        communityGrid.innerHTML = '';
        communitySection.style.display = 'none';
      }
    }
  }

  [catFilter, sizeFilter, priceFilter, matFilter, adjFilter, shipFilter, sortSelect].filter(Boolean).forEach(el => el.addEventListener('change', render));
  searchInput.addEventListener('input', render);

  loadData();
})();
