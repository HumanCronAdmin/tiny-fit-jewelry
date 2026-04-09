// A/B Design Switcher for TinyFit Jewelry
(function() {
  'use strict';

  var cssA = 'css/style.css';
  var cssB = 'css/style-b.css';

  // Detect path depth
  var path = window.location.pathname;
  if (path.includes('/brands/') || path.includes('/size/') || path.includes('/guides/')) {
    cssA = '../css/style.css';
    cssB = '../css/style-b.css';
  }

  // Check URL param or localStorage
  var params = new URLSearchParams(window.location.search);
  var saved = localStorage.getItem('tinyfit-design') || 'a';
  var current = params.get('v') || saved;
  if (current !== 'a' && current !== 'b') current = 'a';

  // Apply on load
  var link = document.getElementById('theme-css');
  if (link && current === 'b') {
    link.href = cssB;
  }
  localStorage.setItem('tinyfit-design', current);

  // ── Inline style overrides for Design B ──
  function applyInlineOverrides(design) {
    // Email CTA section
    var ctaSection = document.querySelector('section[style*="B76E79"]');
    if (ctaSection) {
      if (design === 'b') {
        ctaSection.style.background = '#1A1A1A';
      } else {
        ctaSection.style.background = 'linear-gradient(135deg,#B76E79 0%,#8B5E6B 100%)';
      }
    }

    // Email CTA h2
    var ctaH2 = ctaSection ? ctaSection.querySelector('h2') : null;
    if (ctaH2) {
      if (design === 'b') {
        ctaH2.style.fontFamily = "'DM Sans', sans-serif";
        ctaH2.style.letterSpacing = '-0.02em';
      } else {
        ctaH2.style.fontFamily = "'Playfair Display', Georgia, serif";
        ctaH2.style.letterSpacing = 'normal';
      }
    }

    // Email form button
    var formBtn = ctaSection ? ctaSection.querySelector('button[type="submit"]') : null;
    if (formBtn) {
      if (design === 'b') {
        formBtn.style.borderRadius = '0';
        formBtn.style.background = '#D4AF37';
        formBtn.style.color = '#1A1A1A';
      } else {
        formBtn.style.borderRadius = '50px';
        formBtn.style.background = '#1C1917';
        formBtn.style.color = '#fff';
      }
    }

    // Email input
    var emailInput = document.getElementById('pdf-email');
    if (emailInput) {
      emailInput.style.borderRadius = (design === 'b') ? '0' : '50px';
    }

    // Download button (thank you state)
    var dlBtn = ctaSection ? ctaSection.querySelector('a[href*="pdf"]') : null;
    if (dlBtn) {
      dlBtn.style.borderRadius = (design === 'b') ? '0' : '50px';
    }

    // UGC section (injected by community.js)
    var ugc = document.getElementById('ugc-section');
    if (ugc) {
      // UGC title is the first p inside the div
      var ugcPs = ugc.querySelectorAll('p');
      if (ugcPs.length > 0) {
        ugcPs[0].style.fontFamily = (design === 'b')
          ? "'DM Sans', sans-serif"
          : "'Playfair Display', Georgia, serif";
      }
      var ugcBtns = ugc.querySelectorAll('a');
      ugcBtns.forEach(function(btn, i) {
        if (design === 'b') {
          btn.style.borderRadius = '0';
          if (i === 0) {
            btn.style.background = '#1A1A1A';
            btn.style.boxShadow = 'none';
          }
        } else {
          btn.style.borderRadius = '50px';
          if (i === 0) {
            btn.style.background = 'linear-gradient(135deg,#C4868F,#B76E79,#A25D67)';
            btn.style.boxShadow = '0 2px 10px rgba(183,110,121,0.2)';
          }
        }
      });
    }

    // Accuracy check section (brand pages)
    var accuracy = document.getElementById('accuracy-check');
    if (accuracy) {
      var accPs = accuracy.querySelectorAll('p');
      if (accPs.length > 0) {
        accPs[0].style.fontFamily = (design === 'b')
          ? "'DM Sans', sans-serif"
          : "'Playfair Display', Georgia, serif";
      }
      var accBtns = accuracy.querySelectorAll('button');
      accBtns.forEach(function(btn) {
        btn.style.borderRadius = (design === 'b') ? '0' : '50px';
      });
    }
  }

  // Apply overrides on load (after community.js has injected)
  function applyWhenReady() {
    applyInlineOverrides(current);
    // community.js may inject UGC after this script runs, retry multiple times
    setTimeout(function() { applyInlineOverrides(current); }, 100);
    setTimeout(function() { applyInlineOverrides(current); }, 500);
    setTimeout(function() { applyInlineOverrides(current); }, 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyWhenReady);
  } else {
    applyWhenReady();
  }

  // Build toggle UI
  var bar = document.createElement('div');
  bar.id = 'ab-bar';
  bar.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:9999;display:flex;align-items:center;gap:6px;padding:8px 16px;background:rgba(26,26,26,0.92);backdrop-filter:blur(8px);border-radius:50px;box-shadow:0 4px 24px rgba(0,0,0,0.2);font-family:DM Sans,Inter,sans-serif;font-size:0.78rem;color:#fff;letter-spacing:0.02em;';

  var labelA = document.createElement('button');
  labelA.textContent = 'A: Warm';
  labelA.style.cssText = 'border:none;cursor:pointer;padding:6px 14px;border-radius:50px;font-size:0.78rem;font-family:inherit;font-weight:600;letter-spacing:0.04em;transition:all 0.2s;min-height:32px;';

  var labelB = document.createElement('button');
  labelB.textContent = 'B: Minimal';
  labelB.style.cssText = labelA.style.cssText;

  function updateButtons() {
    if (current === 'a') {
      labelA.style.background = '#D4AF37';
      labelA.style.color = '#1A1A1A';
      labelB.style.background = 'transparent';
      labelB.style.color = '#aaa';
    } else {
      labelA.style.background = 'transparent';
      labelA.style.color = '#aaa';
      labelB.style.background = '#D4AF37';
      labelB.style.color = '#1A1A1A';
    }
  }

  function switchTo(v) {
    current = v;
    localStorage.setItem('tinyfit-design', v);
    if (link) link.href = (v === 'b') ? cssB : cssA;
    updateButtons();
    applyInlineOverrides(v);
    // Track in GA4
    if (typeof gtag === 'function') {
      gtag('event', 'design_switch', { design: v });
    }
  }

  labelA.onclick = function() { switchTo('a'); };
  labelB.onclick = function() { switchTo('b'); };

  bar.appendChild(labelA);
  bar.appendChild(labelB);
  updateButtons();
  document.body.appendChild(bar);
})();
