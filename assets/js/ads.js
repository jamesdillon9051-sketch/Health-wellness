/* ==========================================================================
   HEALTH WELLNESS — ads.js
   Fills the empty .ad-slot divs from the IDs in config.js.

   No ad network is hardcoded into the pages themselves: the markup is just
   empty, sized divs. This file is the single seam where a network gets wired
   in, so switching provider means editing one file, not 111.

   Behaviour when `adClient` is empty (the default): every slot is removed from
   the layout, so an unmonetised site looks finished rather than showing dashed
   boxes. Append ?ads=debug to any URL to see the slots while designing.
   ========================================================================== */
(function () {
  'use strict';

  var cfg   = window.SITE_CONFIG || {};
  var slots = cfg.adSlots || {};
  var debug = /[?&]ads=debug\b/.test(window.location.search);

  /* Which config zone each named slot in the HTML draws its ID from. */
  var ZONE = {
    'header-leaderboard':   'header',
    'category-leaderboard': 'header',
    'post-in-content-1':    'inContent',
    'category-in-content':  'inContent',
    'home-in-content':      'inContent',
    'sidebar-rectangle':    'sidebar',
    'sidebar-skyscraper':   'sidebar',
    'footer-leaderboard':   'footer'
  };

  var nodes = document.querySelectorAll('.ad-slot[data-ad-slot]');
  if (!nodes.length) return;

  if (!cfg.adClient) {
    if (!debug) {
      Array.prototype.forEach.call(nodes, function (el) { el.hidden = true; });
    }
    return;
  }

  /* Load the AdSense library once, after the slots are known to exist. */
  if (!document.querySelector('script[data-adsbygoogle]')) {
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='
          + encodeURIComponent(cfg.adClient);
    s.setAttribute('data-adsbygoogle', '');
    document.head.appendChild(s);
  }

  Array.prototype.forEach.call(nodes, function (el) {
    var id = slots[ZONE[el.getAttribute('data-ad-slot')]];
    if (!id) { if (!debug) el.hidden = true; return; }

    var ins = document.createElement('ins');
    ins.className = 'adsbygoogle';
    ins.style.display = 'block';
    ins.style.width = '100%';
    ins.setAttribute('data-ad-client', cfg.adClient);
    ins.setAttribute('data-ad-slot', id);
    ins.setAttribute('data-ad-format', 'auto');
    ins.setAttribute('data-full-width-responsive', 'true');
    el.appendChild(ins);

    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (err) { /* blocked by an extension, or offline — leave the slot empty */ }
  });
})();
