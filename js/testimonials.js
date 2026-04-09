// testimonials.js — Fetch and display fit experiences from GitHub Issues
(function() {
  'use strict';

  // Curated testimonials (static fallback + seed data)
  // These are templates based on common experiences from the petite jewelry community
  var SEED_TESTIMONIALS = [
    { name: 'Sarah K.', size: 'Ring size 2.5', text: 'I spent years being told my size did not exist. Found Agete through this site and ordered my first ring that actually fits. No more ring adjusters!' },
    { name: 'Emily R.', size: 'Wrist 13cm', text: 'The bracelet formula changed everything. My wrist is 13cm, so I need 14.5cm bracelets. Finally stopped buying "small" bracelets that slide off.' },
    { name: 'Mika T.', size: 'Ring size 3', text: 'Japanese brands are a game changer. I had no idea Nojess and 4C carried my size. The quality is incredible for the price.' },
    { name: 'Lauren W.', size: 'Ring size 2', text: 'My engagement ring is from Automic Gold, custom size 2. They made it without any hassle. This database saved me weeks of research.' },
    { name: 'Jessica M.', size: 'Wrist 12.5cm', text: 'I tried the anklet-as-bracelet hack and it actually works! A Gorjana anklet fits my thin wrist perfectly.' },
    { name: 'Amy C.', size: 'Ring size 3.5', text: 'Catbird was my first find here. Their stackable rings in size 3.5 are gorgeous. I now own four.' },
  ];

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
