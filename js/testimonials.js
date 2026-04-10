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

  // Try to fetch real testimonials from GitHub Issues (label: "fit-experience")
  function fetchGitHubTestimonials(container, limit) {
    fetch('https://api.github.com/repos/HumanCronAdmin/tiny-fit-jewelry/issues?labels=fit-experience&state=closed&per_page=6')
      .then(function(r) { return r.json(); })
      .then(function(issues) {
        if (!Array.isArray(issues) || issues.length === 0) {
          renderTestimonials(container, limit);
          return;
        }
        // Use real issues as testimonials
        var real = issues.map(function(issue) {
          var body = issue.body || '';
          var name = issue.user ? issue.user.login : 'Anonymous';
          // Try to extract ring size from body
          var sizeMatch = body.match(/size\s*(\d+\.?\d*)/i) || body.match(/wrist\s*(\d+\.?\d*)/i);
          var size = sizeMatch ? 'Size ' + sizeMatch[1] : '';
          return { name: name, size: size, text: body.substring(0, 200) };
        });
        // Combine real + seed
        var all = real.concat(SEED_TESTIMONIALS);
        SEED_TESTIMONIALS.length = 0;
        all.forEach(function(t) { SEED_TESTIMONIALS.push(t); });
        renderTestimonials(container, limit);
      })
      .catch(function() {
        renderTestimonials(container, limit);
      });
  }

  // Auto-insert on index.html
  if (window.location.pathname.endsWith('index.html') || window.location.pathname.endsWith('/tiny-fit-jewelry/')) {
    var target = document.querySelector('#testimonials-container');
    if (target) {
      fetchGitHubTestimonials(target, 3);
    }
  }

  // Expose for manual use on other pages
  window.TinyFitTestimonials = { render: renderTestimonials, fetch: fetchGitHubTestimonials };
})();
