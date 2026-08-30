/* ==========================================================================
   HEALTH WELLNESS — config.js
   THE ONLY FILE YOU EDIT TO CONNECT SERVICES.

   Everything the site needs from the outside world is a value in here.
   Fill a value in and the feature switches on across all 111 pages; leave it
   empty and that feature stays visibly, honestly off rather than failing
   silently. Loaded before main.js on every page.
   ========================================================================== */
window.SITE_CONFIG = {

  /* -- 1. Forms ----------------------------------------------------------
     Create two forms at https://formspree.io (free tier is fine). Each gives
     you an 8-character ID from its endpoint URL:
         https://formspree.io/f/xayzbwqr   ->   'xayzbwqr'
     Paste them here. Submissions then arrive in your Formspree inbox and are
     forwarded to the email you registered with.                            */
  formspreeContactId: '',
  formspreeSignupId:  '',

  /* -- 2. Ads ------------------------------------------------------------
     Your AdSense publisher ID ('ca-pub-0000000000000000') and the slot ID for
     each zone, from AdSense > Ads > By ad unit. Any zone left empty renders
     nothing at all — no gap, no placeholder.
     Using a different network? See assets/js/ads.js.                       */
  adClient: '',
  adSlots: {
    header:    '',
    inContent: '',
    sidebar:   '',
    footer:    ''
  },

  /* -- 3. Analytics ------------------------------------------------------
     Optional. A Plausible/Fathom/GA4 snippet can go in ads.js the same way. */
  analyticsDomain: ''
};
