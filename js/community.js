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
    + '<div id="ugc-section" style="text-align:center;padding:32px 20px;margin:28px auto;max-width:560px;background:transparent;border-top:1px solid #E7E5E4;border-bottom:1px solid #E7E5E4;border-left:none;border-right:none;border-radius:0;">'
    + '  <p style="font-family:Playfair Display,Georgia,serif;font-weight:700;font-size:1.05rem;color:#1C1917;margin:0 0 8px;letter-spacing:-0.01em;">Help Us Stay Accurate</p>'
    + '  <p style="font-size:0.84rem;color:#78716C;margin:0 0 20px;line-height:1.6;">Real experiences from real people make this database better than any AI can.</p>'
    + '  <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">'
    + '    <a href="mailto:korumono2929@gmail.com?subject=Fit%20Experience&body=Brand:%0ARing%20size:%0AWrist%20size:%0AHow%20it%20fits:%0A"'
    + '       style="display:inline-block;padding:11px 24px;background:linear-gradient(135deg,#C4868F,#B76E79,#A25D67);color:#fff;border-radius:50px;text-decoration:none;font-weight:600;font-size:0.8rem;min-height:44px;line-height:22px;letter-spacing:0.04em;text-transform:uppercase;box-shadow:0 2px 10px rgba(183,110,121,0.2);">'
    + '       Share My Fit Experience</a>'
    + '    <a href="mailto:korumono2929@gmail.com?subject=Brand%20Suggestion&body=Brand%20name:%0AMinimum%20ring%20size:%0AWebsite%20URL:%0A"'
    + '       style="display:inline-block;padding:11px 24px;background:transparent;color:#1C1917;border:1.5px solid #1C1917;border-radius:50px;text-decoration:none;font-weight:600;font-size:0.8rem;min-height:44px;line-height:22px;letter-spacing:0.04em;text-transform:uppercase;">'
    + '       Suggest a Brand</a>'
    + '  </div>'
    + '  <p style="font-size:0.72rem;color:#aaa;margin:14px 0 0;letter-spacing:0.02em;">Your experience helps others find jewelry that actually fits.</p>'
    + '</div>';

  // ── Brand page: "Is this info accurate?" ──
  var isBrandPage = path.includes('/brands/');
  var brandAccuracyHTML = '';
  if (isBrandPage) {
    var brandName = document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : 'this brand';
    brandAccuracyHTML = ''
      + '<div id="accuracy-check" style="text-align:center;padding:24px 20px;margin:0 auto 16px;max-width:560px;background:transparent;border-top:1px solid #E7E5E4;border-bottom:1px solid #E7E5E4;border-radius:0;">'
      + '  <p style="font-family:Playfair Display,Georgia,serif;font-weight:600;font-size:0.95rem;color:#1C1917;margin:0 0 12px;">Is our size info for ' + brandName + ' still accurate?</p>'
      + '  <div style="display:flex;gap:12px;justify-content:center;">'
      + '    <button onclick="reportAccuracy(true)" style="padding:10px 28px;background:#22C55E;color:#fff;border:none;border-radius:50px;font-weight:600;font-size:0.82rem;cursor:pointer;min-height:44px;letter-spacing:0.03em;text-transform:uppercase;">Yes, accurate</button>'
      + '    <button onclick="reportAccuracy(false)" style="padding:10px 28px;background:#EF4444;color:#fff;border:none;border-radius:50px;font-weight:600;font-size:0.82rem;cursor:pointer;min-height:44px;letter-spacing:0.03em;text-transform:uppercase;">No, outdated</button>'
      + '  </div>'
      + '  <p id="accuracy-thanks" style="font-size:0.82rem;color:#22C55E;margin:10px 0 0;display:none;">Thank you! Your feedback helps keep our data reliable.</p>'
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
        + '<a href="mailto:korumono2929@gmail.com?subject=Outdated%20info:%20' + encodeURIComponent(brandName)
        + '&body=The%20size%20info%20for%20' + encodeURIComponent(brandName) + '%20seems%20outdated.%0A%0AWhat%20changed:%0A" '
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
