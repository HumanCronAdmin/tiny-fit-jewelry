// community.js — UGC + cross-site footer injection
(function() {
  'use strict';

  // Detect path depth for relative links
  var depth = 0;
  var path = window.location.pathname;
  if (path.includes('/brands/') || path.includes('/size/') || path.includes('/guides/')) {
    depth = 1;
  }
  var prefix = depth === 1 ? '../' : '';

  // ── UGC: "Share Your Fit Experience" ──
  var ugcHTML = ''
    + '<div id="ugc-section" style="text-align:center;padding:28px 16px;margin:24px auto;max-width:620px;background:#FAF5F6;border:1px solid #E7E5E4;border-radius:12px;">'
    + '  <p style="font-weight:700;font-size:1rem;color:#1C1917;margin:0 0 6px;">Help Us Stay Accurate</p>'
    + '  <p style="font-size:0.85rem;color:#78716C;margin:0 0 16px;line-height:1.5;">Real experiences from real people make this database better than any AI can. Share what you know.</p>'
    + '  <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">'
    + '    <a href="https://github.com/HumanCronAdmin/tiny-fit-jewelry/issues/new?template=fit_experience.yml&title=Fit+Experience" target="_blank" rel="noopener" '
    + '       style="display:inline-block;padding:10px 20px;background:#B76E79;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;min-height:44px;line-height:24px;">'
    + '       Share My Fit Experience</a>'
    + '    <a href="https://github.com/HumanCronAdmin/tiny-fit-jewelry/issues/new?template=brand_suggestion.yml&title=Brand+Suggestion" target="_blank" rel="noopener" '
    + '       style="display:inline-block;padding:10px 20px;background:#1C1917;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;min-height:44px;line-height:24px;">'
    + '       Suggest a Brand</a>'
    + '  </div>'
    + '  <p style="font-size:0.75rem;color:#aaa;margin:10px 0 0;">Your experience helps others find jewelry that actually fits.</p>'
    + '</div>';

  // ── Brand page: "Is this info accurate?" ──
  var isBrandPage = path.includes('/brands/');
  var brandAccuracyHTML = '';
  if (isBrandPage) {
    var brandName = document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : 'this brand';
    brandAccuracyHTML = ''
      + '<div id="accuracy-check" style="text-align:center;padding:20px 16px;margin:0 auto 16px;max-width:620px;background:#F5F5F4;border:1px solid #E7E5E4;border-radius:12px;">'
      + '  <p style="font-weight:600;font-size:0.92rem;color:#1C1917;margin:0 0 10px;">Is our size info for ' + brandName + ' still accurate?</p>'
      + '  <div style="display:flex;gap:12px;justify-content:center;">'
      + '    <button onclick="reportAccuracy(true)" style="padding:10px 28px;background:#22C55E;color:#fff;border:none;border-radius:8px;font-weight:600;font-size:0.88rem;cursor:pointer;min-height:44px;">Yes, accurate</button>'
      + '    <button onclick="reportAccuracy(false)" style="padding:10px 28px;background:#EF4444;color:#fff;border:none;border-radius:8px;font-weight:600;font-size:0.88rem;cursor:pointer;min-height:44px;">No, outdated</button>'
      + '  </div>'
      + '  <p id="accuracy-thanks" style="font-size:0.82rem;color:#22C55E;margin:8px 0 0;display:none;">Thank you! Your feedback helps keep our data reliable.</p>'
      + '</div>';
  }

  // GA4 event for accuracy feedback
  window.reportAccuracy = function(accurate) {
    var brandName = document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : 'unknown';
    if (typeof gtag === 'function') {
      gtag('event', 'accuracy_feedback', {
        brand: brandName,
        accurate: accurate ? 'yes' : 'no'
      });
    }
    var el = document.getElementById('accuracy-check');
    if (accurate) {
      document.getElementById('accuracy-thanks').style.display = 'block';
      setTimeout(function() { el.style.opacity = '0.6'; }, 1500);
    } else {
      el.innerHTML = '<p style="font-weight:600;font-size:0.92rem;color:#1C1917;margin:0 0 10px;">Thanks for letting us know!</p>'
        + '<a href="https://github.com/HumanCronAdmin/tiny-fit-jewelry/issues/new?title=Outdated+info:+' + encodeURIComponent(brandName)
        + '&body=The+size+info+for+' + encodeURIComponent(brandName) + '+seems+outdated.%0A%0AWhat+changed:%0A" target="_blank" rel="noopener" '
        + 'style="display:inline-block;padding:10px 20px;background:#B76E79;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;min-height:44px;line-height:24px;">Tell Us What Changed</a>';
    }
  };

  // No cross-site links — keep TinyFit's jewelry world self-contained

  // ── Inject into page ──
  var footer = document.querySelector('footer.footer');
  if (!footer) return;

  // Remove old GitHub-based feedback sections (if present)
  var oldFeedback = footer.querySelectorAll('div');
  oldFeedback.forEach(function(div) {
    if (div.textContent.includes('Know a brand we are missing?') && div.textContent.includes('GitHub issue')) {
      div.remove();
    }
  });

  // Insert: brand accuracy (if brand page) → UGC → cross-site
  var insertPoint = footer;
  var wrapper = document.createElement('div');
  wrapper.innerHTML = brandAccuracyHTML + ugcHTML;

  // Insert after footer's closing div, before </footer>
  footer.appendChild(wrapper);
})();
