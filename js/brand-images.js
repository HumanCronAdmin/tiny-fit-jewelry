// brand-images.js — Add brand logos and visual cards to brand pages
// Uses Google Favicon API (copyright-safe, no hotlinking issues)
(function() {
  'use strict';
  if (!window.location.pathname.includes('/brands/')) return;

  // Get brand data from the page
  var h1 = document.querySelector('h1');
  if (!h1) return;

  var shopLink = document.querySelector('a.btn[href*="://"]');
  if (!shopLink) return;

  var brandUrl = shopLink.href;
  var domain = brandUrl.replace(/https?:\/\//, '').split('/')[0];

  // Create visual brand header
  var header = document.createElement('div');
  header.style.cssText = 'display:flex;align-items:center;gap:16px;margin:16px 0 20px;padding:20px;background:#fff;border:1px solid #E7E5E4;border-radius:12px;';

  // Brand favicon/logo (128px from Google API)
  var logoSize = 64;
  header.innerHTML = ''
    + '<img src="https://www.google.com/s2/favicons?domain=' + domain + '&sz=128"'
    + ' alt="' + h1.textContent.split(' Size')[0] + ' logo"'
    + ' width="' + logoSize + '" height="' + logoSize + '"'
    + ' style="border-radius:12px;background:#f5f5f4;flex-shrink:0;"'
    + ' onerror="this.style.display=\'none\'">'
    + '<div>'
    + '<div style="font-weight:800;font-size:1.1rem;color:#1C1917;">' + h1.textContent.split(' Size')[0].replace(' Petite Jewelry', '') + '</div>'
    + '<a href="' + brandUrl + '" target="_blank" rel="noopener" style="font-size:0.85rem;color:#B76E79;text-decoration:none;">' + domain + ' &rarr;</a>'
    + '</div>';

  // Insert after h1 and meta line
  var metaP = h1.nextElementSibling;
  if (metaP && metaP.classList.contains('meta')) {
    metaP.parentNode.insertBefore(header, metaP.nextSibling);
  } else {
    h1.parentNode.insertBefore(header, h1.nextSibling);
  }

  // Also add to database page brand cards
  if (window.TinyFitBrandImages) {
    window.TinyFitBrandImages.addLogos();
  }
})();

// For database.html — add logos to brand cards
window.TinyFitBrandImages = {
  addLogos: function() {
    var cards = document.querySelectorAll('.brand-card, [data-brand-url]');
    cards.forEach(function(card) {
      var link = card.querySelector('a[href*="://"]');
      if (!link) return;
      var domain = link.href.replace(/https?:\/\//, '').split('/')[0];
      var img = document.createElement('img');
      img.src = 'https://www.google.com/s2/favicons?domain=' + domain + '&sz=64';
      img.alt = '';
      img.width = 32;
      img.height = 32;
      img.style.cssText = 'border-radius:6px;background:#f5f5f4;vertical-align:middle;margin-right:8px;';
      img.onerror = function() { this.style.display = 'none'; };
      var title = card.querySelector('h3, h2, .brand-name');
      if (title) title.prepend(img);
    });
  }
};
