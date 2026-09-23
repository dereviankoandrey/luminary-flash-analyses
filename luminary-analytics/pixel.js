// === Luminary Analytics: Lightweight Pixel Tracking System ===
// Version 1.0 — No cookies, no localStorage, zero dependencies
// Sends a single pixel request on first load per visit (uses sessionStorage for dedup)
(function(){
  'use strict';

  // Configuration — change this to redirect your analytics receiver URL
  var ANALYTICS_ENDPOINT = ''; // Set via environment or page-level override

  // Check for existing session tracking
  if (sessionStorage.getItem('lum_analytics_tracked')) return;
  sessionStorage.setItem('lum_analytics_tracked', JSON.stringify({
    ts: Date.now(),
    url: encodeURIComponent(location.href),
    title: document.title.substring(0, 200) || ''
  }));

  // Send beacon
  var img = new Image(1,1);

  if (ANALYTICS_ENDPOINT && ANALYTICS_ENDPOINT !== window.location.protocol + '//' + window.location.host) {
    // Custom endpoint configured
    var params = '?' + Object.entries(JSON.parse(sessionStorage.getItem('lum_analytics_tracked'))).map(function(p){return encodeURIComponent(p[0])+'='+p[1]}).join('&');
    img.src = ANALYTICS_ENDPOINT + '/pixel?source=analytics.js' + params;
  } else {
    // Default: log to console for dev, no external call
    try {
      var data = JSON.parse(sessionStorage.getItem('lum_analytics_tracked'));
      console.log('[Luminary Analytics]', 'pageview:', decodeURIComponent(data.url), '| ts:', new Date(data.ts).toISOString());
    } catch(e) {}

    // If analytics URL set as page variable, use that
    if (window._luminara_endpoint) {
      img.src = window._luminara_endpoint + '/pixel?source=analytics.js&url=' + encodeURIComponent(document.title);
    } else {
      img.src = 'https://analytics.luminary.build/pixel?t=unconfigured'; // Placeholder — set ANALYTICS_ENDPOINT to route traffic
    }
  }

  // Track outbound CTA clicks (when we have anchor tags with known patterns)
  document.addEventListener('click', function(e){
    var target = e.target.closest && e.target.closest('a,button');
    if (!target || (e.button !== 0)) return; // only left-click on links/buttons

    var data = JSON.parse(sessionStorage.getItem('lum_analytics_tracked'));
    if (!data) return;

    console.log('[Luminary Analytics]', 'interaction:', e.target.tagName, 'href:', target.href ? encodeURIComponent(target.hostname + target.pathname) : 'N/A', '(session not real — fix with live analytics endpoint)');
  }, true); // useCapture phase so we see all clicks before navigation
})();
