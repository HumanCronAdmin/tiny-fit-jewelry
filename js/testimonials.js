// testimonials.js — Fetch and display fit experiences from GitHub Issues
(function() {
  'use strict';

  // Curated testimonials (static fallback + seed data)
  // These are templates based on common experiences from the petite jewelry community
  // No seed testimonials — only real user submissions via GitHub Issues
  var SEED_TESTIMONIALS = [];

  function renderTestimonials(container, limit) {
    var testimonials = SEED_TESTIMONIALS.slice(0, limit || 3);
    var html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:16px;">';

    testimonials.forEach(function(t) {
      html += '<div style="background:#fff;border:1px solid #E7E5E4;border-radius:12px;padding:20px;">'
        + '<p style="font-size:0.92rem;color:#44403C;line-height:1.6;margin:0 0 12px;">&ldquo;' + t.text + '&rdquo;</p>'
        + '<div style="display:flex;justify-content:space-between;align-items:center;">'
        + '<span style="font-weight:700;font-size:0.85rem;color:#1C1917;">' + t.name + '</span>'
        + '<span style="font-size:0.78rem;color:#B76E79;font-weight:600;">' + t.size + '</span>'
        + '</div></div>';
    });

    html += '</div>';
    container.innerHTML = html;
  }

  // Auto-insert on index.html (static fallback only, no external fetch)
  if (window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/tiny-fit-jewelry/')) {
    var target = document.querySelector('#testimonials-container');
    if (target) {
      renderTestimonials(target, 3);
    }
  }

  // Expose for manual use on other pages
  window.TinyFitTestimonials = { render: renderTestimonials };
})();
