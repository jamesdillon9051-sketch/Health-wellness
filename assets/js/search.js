/* ==========================================================================
   HEALTH WELLNESS — search.js
   Client-side search over a prebuilt index. No dependencies, no build step.

   The index (assets/search-index.json, ~61 KB) is fetched lazily the first
   time search is opened, so it costs nothing on a normal page view. It holds
   each post's title, standfirst, section headings and target keyword — not the
   body text, which would be several megabytes.

   Progressive enhancement: the header button is a real link to search.html,
   which lists every post grouped by section and works with no JavaScript at
   all. This file upgrades that into an overlay and a live filter.
   ========================================================================== */
(function () {
  'use strict';

  /* Path depth differs between /, /posts/ and /categories/, so derive the
     prefix from a link the page already carries rather than guessing. */
  var css = document.querySelector('link[href*="assets/css/style.css"]');
  var BASE = css ? css.getAttribute('href').split('assets/')[0] : '';

  var index = null, loading = null;

  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch(BASE + 'assets/search-index.json')
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (d) { index = d; return d; });
    return loading;
  }

  function tokens(q) {
    return q.toLowerCase().split(/[^a-z0-9]+/).filter(function (t) { return t.length > 1; });
  }

  /* Every token must appear somewhere, so "quiet apartment" does not match a
     post that only mentions apartments. Field weights decide the order. */
  function score(post, toks, raw) {
    var title = post.t.toLowerCase(),
        desc = (post.d || '').toLowerCase(),
        key = (post.k || '').toLowerCase(),
        heads = (post.h || []).join(' ').toLowerCase(),
        cat = (post.c || '').toLowerCase(),
        total = 0;

    if (raw.length > 2 && title.indexOf(raw) !== -1) total += 120;
    if (raw.length > 2 && key.indexOf(raw) !== -1) total += 60;

    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], hit = 0;
      if (title.indexOf(t) !== -1) hit += 40;
      if (key.indexOf(t) !== -1) hit += 30;
      if (heads.indexOf(t) !== -1) hit += 15;
      if (desc.indexOf(t) !== -1) hit += 10;
      if (cat.indexOf(t) !== -1) hit += 8;
      if (!hit) return 0;                 // one missing token rules the post out
      total += hit;
    }
    if (post.g) total += 12;              // pillar guides surface first on ties
    return total;
  }

  function search(q) {
    var raw = q.trim().toLowerCase(), toks = tokens(raw);
    if (!toks.length || !index) return [];
    return index
      .map(function (p) { return { p: p, n: score(p, toks, raw) }; })
      .filter(function (r) { return r.n > 0; })
      .sort(function (a, b) { return b.n - a.n || a.p.t.localeCompare(b.p.t); })
      .slice(0, 30)
      .map(function (r) { return r.p; });
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function mark(text, toks) {
    var out = esc(text);
    toks.forEach(function (t) {
      // Anchor to a word start: "flat" should highlight in "Flats" but not in
      // the middle of "conflates".
      out = out.replace(
        new RegExp('\\b(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'),
        '<mark>$1</mark>');
    });
    return out;
  }

  function render(list, q, into) {
    var toks = tokens(q);
    if (!q.trim()) {
      into.innerHTML = '<p class="search__hint">Type to search 100 guides — try ' +
        '<em>push up</em>, <em>small flat</em>, <em>protein</em> or <em>sleep</em>.</p>';
      return;
    }
    if (!list.length) {
      into.innerHTML = '<p class="search__hint">Nothing matches <strong>' + esc(q) +
        '</strong>. Try a single word, or browse a section from the menu.</p>';
      return;
    }
    into.innerHTML = '<p class="search__count">' + list.length +
      (list.length === 1 ? ' guide' : ' guides') + '</p><ul class="search__list">' +
      list.map(function (p) {
        return '<li><a href="' + BASE + 'posts/' + p.s + '.html" data-pillar="' + p.p + '">' +
          '<span class="search__cat">' + esc(p.c) + '</span>' +
          '<span class="search__title">' + mark(p.t, toks) + '</span>' +
          '<span class="search__desc">' + mark(p.d, toks) + '</span></a></li>';
      }).join('') + '</ul>';
  }

  /* --- Overlay ----------------------------------------------------------- */
  var overlay = null, input = null, results = null, lastFocus = null;

  function build() {
    overlay = document.createElement('div');
    overlay.className = 'search';
    overlay.hidden = true;
    overlay.innerHTML =
      '<div class="search__panel" role="dialog" aria-modal="true" aria-label="Search guides">' +
      '  <form class="search__form" role="search">' +
      '    <label class="visually-hidden" for="search-input">Search guides</label>' +
      '    <input id="search-input" type="search" autocomplete="off" placeholder="Search 100 guides…">' +
      '    <button type="button" class="search__close" aria-label="Close search">Esc</button>' +
      '  </form>' +
      '  <div class="search__results" aria-live="polite"></div>' +
      '</div>';
    document.body.appendChild(overlay);
    input = overlay.querySelector('input');
    results = overlay.querySelector('.search__results');

    overlay.querySelector('form').addEventListener('submit', function (e) { e.preventDefault(); });
    overlay.querySelector('.search__close').addEventListener('click', close);
    overlay.addEventListener('mousedown', function (e) { if (e.target === overlay) close(); });
    input.addEventListener('input', function () {
      render(search(input.value), input.value, results);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowDown' && e.key !== 'Enter') return;
      var first = results.querySelector('a');
      if (!first) return;
      e.preventDefault();
      if (e.key === 'Enter') first.click(); else first.focus();
    });
    results.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      var links = Array.prototype.slice.call(results.querySelectorAll('a'));
      var i = links.indexOf(document.activeElement);
      e.preventDefault();
      if (e.key === 'ArrowUp' && i <= 0) { input.focus(); return; }
      var next = links[e.key === 'ArrowDown' ? i + 1 : i - 1];
      if (next) next.focus();
    });
  }

  function open(e) {
    if (e) e.preventDefault();
    if (!overlay) build();
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    input.focus();
    load().then(function () { render(search(input.value), input.value, results); })
          .catch(function () {
            results.innerHTML = '<p class="search__hint">Search could not load. ' +
              '<a href="' + BASE + 'search.html">Browse all guides instead</a>.</p>';
          });
  }

  function close() {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    document.documentElement.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') return close();
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) return open(e);
    if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) open(e);
  });

  Array.prototype.forEach.call(document.querySelectorAll('[data-search]'), function (b) {
    b.addEventListener('click', open);
  });

  /* --- search.html: same engine, rendered inline --------------------------- */
  var page = document.querySelector('[data-search-page]');
  if (page) {
    var pin = page.querySelector('input'), pout = page.querySelector('.search__results');
    var browse = document.querySelector('[data-search-browse]');
    page.hidden = false;
    load().then(function () {
      var q = new URLSearchParams(location.search).get('q') || '';
      pin.value = q;
      if (q) { if (browse) browse.hidden = true; render(search(q), q, pout); }
      pin.focus();
    });
    pin.addEventListener('input', function () {
      if (browse) browse.hidden = !!pin.value.trim();
      render(search(pin.value), pin.value, pout);
    });
    page.querySelector('form').addEventListener('submit', function (e) { e.preventDefault(); });
  }
})();
