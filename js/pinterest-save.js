/* Pinterest Save Button — floating button on every page */
(function() {
  // Pinterest SDK
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://assets.pinterest.com/js/pinit.js';
  s.setAttribute('data-pin-hover', 'true');
  s.setAttribute('data-pin-tall', 'true');
  document.body.appendChild(s);

  // Add a fixed "Pin It" floating button (bottom-right)
  var btn = document.createElement('a');
  btn.href = 'https://www.pinterest.com/pin/create/button/';
  btn.setAttribute('data-pin-do', 'buttonBookmark');
  btn.setAttribute('data-pin-tall', 'true');
  btn.setAttribute('data-pin-round', 'true');
  btn.style.cssText = 'position:fixed;bottom:80px;right:20px;z-index:9999;opacity:0.9;';
  btn.title = 'Save to Pinterest';
  document.body.appendChild(btn);
})();
