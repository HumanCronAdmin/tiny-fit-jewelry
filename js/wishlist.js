// wishlist.js — Save favorite brands to localStorage
(function() {
  'use strict';

  var STORAGE_KEY = 'tinyfit_wishlist';

  function getWishlist() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; }
    catch(e) { return []; }
  }

  function saveWishlist(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function isInWishlist(brand) {
    return getWishlist().indexOf(brand) !== -1;
  }

  function toggleWishlist(brand) {
    var list = getWishlist();
    var idx = list.indexOf(brand);
    if (idx === -1) { list.push(brand); } else { list.splice(idx, 1); }
    saveWishlist(list);
    return idx === -1; // true = added
  }

  // Add heart button to brand pages
  var path = window.location.pathname;
  if (path.includes('/brands/')) {
    var h1 = document.querySelector('h1');
    if (!h1) return;
    var brandName = h1.textContent.trim();
    var saved = isInWishlist(brandName);

    var btn = document.createElement('button');
    btn.id = 'wishlist-btn';
    btn.setAttribute('aria-label', 'Save to favorites');
    btn.style.cssText = 'background:none;border:2px solid #B76E79;border-radius:8px;padding:8px 16px;font-size:0.9rem;font-weight:600;cursor:pointer;margin-left:12px;color:#B76E79;font-family:inherit;vertical-align:middle;';
    btn.innerHTML = saved ? '&#9829; Saved' : '&#9825; Save';
    if (saved) { btn.style.background = '#B76E79'; btn.style.color = '#fff'; }

    btn.addEventListener('click', function() {
      var added = toggleWishlist(brandName);
      btn.innerHTML = added ? '&#9829; Saved' : '&#9825; Save';
      btn.style.background = added ? '#B76E79' : 'none';
      btn.style.color = added ? '#fff' : '#B76E79';
      if (typeof gtag === 'function') {
        gtag('event', 'wishlist_toggle', { brand: brandName, action: added ? 'add' : 'remove' });
      }
    });

    h1.parentNode.insertBefore(btn, h1.nextSibling);
  }

  // Add wishlist count to nav (if items saved)
  var list = getWishlist();
  if (list.length > 0) {
    var navLinks = document.querySelector('.nav-links');
    if (navLinks) {
      var depth = (path.includes('/brands/') || path.includes('/size/') || path.includes('/guides/')) ? '../' : '';
      var wishLink = document.createElement('a');
      wishLink.href = depth + 'wishlist.html';
      wishLink.innerHTML = '&#9829; ' + list.length;
      wishLink.style.cssText = 'color:#B76E79;font-weight:700;';
      wishLink.title = list.length + ' saved brands';
      // Append as <li> if nav uses <ul>, otherwise as <a>
      if (navLinks.tagName === 'UL') {
        var li = document.createElement('li');
        li.appendChild(wishLink);
        navLinks.appendChild(li);
      } else {
        navLinks.appendChild(wishLink);
      }
    }
  }

  window.TinyFitWishlist = { get: getWishlist, toggle: toggleWishlist, has: isInWishlist };
})();
