/* ==========================================================================
   SIX SQUARE FEET — main.js
   Vanilla JS, no dependencies. Loaded with `defer` on every page.
   Every feature is progressive enhancement: the site works fully without it.
   ========================================================================== */
(function () {
  'use strict';

  /* --- 1. Mobile navigation ---------------------------------------------- */
  var toggle = document.querySelector('.nav-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  if (toggle && mobileNav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      mobileNav.hidden = open;
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        toggle.setAttribute('aria-expanded', 'false');
        mobileNav.hidden = true;
        toggle.focus();
      }
    });
  }

  /* --- 2. Reading progress bar (posts only) ------------------------------ */
  var article = document.querySelector('article.post');
  var bar = document.querySelector('.reading-progress');

  if (article && bar) {
    var updateProgress = function () {
      var top = article.offsetTop;
      var height = article.offsetHeight - window.innerHeight;
      var scrolled = window.scrollY - top;
      var pct = height > 0 ? Math.min(Math.max(scrolled / height, 0), 1) : 0;
      bar.style.width = (pct * 100).toFixed(2) + '%';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
    updateProgress();
  }

  /* --- 3. Active heading highlight in the table of contents -------------- */
  var tocLinks = document.querySelectorAll('.toc a[href^="#"]');

  if (tocLinks.length && 'IntersectionObserver' in window) {
    var linkFor = {};
    var targets = [];

    Array.prototype.forEach.call(tocLinks, function (link) {
      var id = link.getAttribute('href').slice(1);
      var el = document.getElementById(id);
      if (el) {
        linkFor[id] = link;
        targets.push(el);
      }
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = linkFor[entry.target.id];
        if (!link) return;
        if (entry.isIntersecting) {
          Array.prototype.forEach.call(tocLinks, function (l) { l.classList.remove('is-active'); });
          link.classList.add('is-active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });

    targets.forEach(function (t) { observer.observe(t); });
  }

  /* --- 4. Share buttons --------------------------------------------------- */
  var shareUrl = window.location.href;
  var shareTitle = document.title;

  var nativeBtn = document.querySelector('[data-share="native"]');
  if (nativeBtn) {
    if (navigator.share) {
      nativeBtn.addEventListener('click', function () {
        navigator.share({ title: shareTitle, url: shareUrl }).catch(function () { /* dismissed */ });
      });
    } else {
      nativeBtn.hidden = true;
    }
  }

  var copyBtn = document.querySelector('[data-share="copy"]');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var done = function () {
        var original = copyBtn.textContent;
        copyBtn.textContent = 'Link copied';
        setTimeout(function () { copyBtn.textContent = original; }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareUrl).then(done, function () {});
      }
    });
  }

  /* --- 5. Back to top ----------------------------------------------------- */
  var toTop = document.querySelector('.to-top');
  if (toTop) {
    window.addEventListener('scroll', function () {
      toTop.classList.toggle('is-visible', window.scrollY > 900);
    }, { passive: true });

    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* --- 6. Footer year ------------------------------------------------------ */
  var year = document.querySelector('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());

  /* --- 7. Harden external links -------------------------------------------- */
  var links = document.querySelectorAll('a[href^="http"]');
  Array.prototype.forEach.call(links, function (link) {
    if (link.hostname && link.hostname !== window.location.hostname) {
      link.setAttribute('rel', 'noopener noreferrer');
      link.setAttribute('target', '_blank');
    }
  });

  /* --- 8. Email signup placeholder ----------------------------------------
     No email service is wired up yet. Until you connect one (ConvertKit,
     Buttondown, Mailchimp, Beehiiv), intercept the submit so nothing is lost
     silently. Delete this block once the form `action` points at a real
     endpoint.
     ------------------------------------------------------------------------ */
  var forms = document.querySelectorAll('.signup__form[data-placeholder]');
  Array.prototype.forEach.call(forms, function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.parentNode.querySelector('.signup__note');
      if (note) note.textContent = 'Signup is not connected yet — add your email service endpoint to this form.';
    });
  });
})();
