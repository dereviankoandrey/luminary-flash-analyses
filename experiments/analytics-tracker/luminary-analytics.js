// Luminary Analytics Tracker v1.0 — Free, no-key, no-PII pageview counter
// Uses countapi.xyz (free tier) + localStorage for session tracking
(function(){
  var site = 'luminary-ventures';
  
  // Unique session ID
  if(!localStorage.getItem('lum_sid')){
    localStorage.setItem('lum_sid', Math.random().toString(36).substr(2,12));
  }
  
  // Increment pageview counter
  try {
    var path = location.pathname.split('/').pop() || 'index';
    fetch('https://api.countapi.xyz/hit/'+site+'/'+path)
      .catch(function(){ /* non-critical: don't break the page */ });
  } catch(e){}
  
  // Log to console for debugging (visible in browser DevTools)
  console.log('[Luminary Analytics] Pageview tracked:', {
    url: location.href,
    sid: localStorage.getItem('lum_sid'),
    pv: parseInt(localStorage.getItem('lum_pv')||'0')+1
  });
})();
