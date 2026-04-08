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
    + '    <a href="mailto:petitedevlog@gmail.com?subject=My%20Fit%20Experience&body=Hi!%20Here%27s%20my%20experience:%0A%0AMy%20ring%20size%20(US):%0AMy%20wrist%20size%20(cm):%0ABrand%20I%20tried:%0ADid%20it%20fit%3F%20(yes/no):%0ANotes:%0A" '
    + '       style="display:inline-block;padding:10px 20px;background:#B76E79;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;min-height:44px;line-height:24px;">'
    + '       Share My Fit Experience</a>'
    + '    <a href="mailto:petitedevlog@gmail.com?subject=Brand%20Suggestion&body=Brand%20name:%0AMinimum%20ring%20size:%0AMinimum%20bracelet%20length:%0AWebsite%20URL:%0AAnything%20else:%0A" '
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
        + '<a href="mailto:petitedevlog@gmail.com?subject=Outdated%20info:%20' + encodeURIComponent(brandName)
        + '&body=Hi!%20The%20size%20info%20for%20' + encodeURIComponent(brandName) + '%20seems%20outdated.%0A%0AWhat%20changed:%0A" '
        + 'style="display:inline-block;padding:10px 20px;background:#B76E79;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.88rem;min-height:44px;line-height:24px;">Tell Us What Changed</a>';
    }
  };

  // ── Cross-site footer: "More Free Tools" ──
  var crossSiteHTML = ''
    + '<div id="cross-site-footer" style="text-align:center;padding:28px 16px;margin:24px auto;max-width:700px;border-top:1px solid #E7E5E4;">'
    + '  <p style="font-weight:700;font-size:0.95rem;color:#1C1917;margin:0 0 6px;">More Free Tools</p>'
    + '  <p style="font-size:0.82rem;color:#78716C;margin:0 0 16px;">Built by the same creator. All free, no signup required.</p>'
    + '  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;max-width:600px;margin:0 auto;">'
    + '    <a href="https://humancronadmin.github.io/japan-size-converter/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Japan Size Converter</a>'
    + '    <a href="https://humancronadmin.github.io/japan-pro-finder/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Japan Pro Finder</a>'
    + '    <a href="https://humancronadmin.github.io/japan-tax-calculator/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Japan Tax Calculator</a>'
    + '    <a href="https://humancronadmin.github.io/money-transfer-japan/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Money Transfer Japan</a>'
    + '    <a href="https://humancronadmin.github.io/image2pdf/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Image to PDF</a>'
    + '    <a href="https://humancronadmin.github.io/foreign-grocery-finder/" target="_blank" rel="noopener" '
    + '       style="display:block;padding:12px 10px;background:#F5F5F4;border-radius:8px;text-decoration:none;color:#1C1917;font-size:0.82rem;font-weight:500;transition:background .2s;"'
    + '       onmouseover="this.style.background=\'#E7E5E4\'" onmouseout="this.style.background=\'#F5F5F4\'">'
    + '       Foreign Grocery Finder</a>'
    + '  </div>'
    + '  <p style="font-size:0.75rem;color:#aaa;margin:12px 0 0;"><a href="https://github.com/humancronadmin" target="_blank" rel="noopener" style="color:#B76E79;text-decoration:none;">See all projects on GitHub &rarr;</a></p>'
    + '</div>';

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
  wrapper.innerHTML = brandAccuracyHTML + ugcHTML + crossSiteHTML;

  // Insert after footer's closing div, before </footer>
  footer.appendChild(wrapper);
})();
