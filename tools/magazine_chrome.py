# -*- coding: utf-8 -*-
"""Rebuild the shared header as news-magazine chrome, on every page.

Adds the three bands a magazine front page runs above its content:
  ticker       breaking-news strip with live headlines
  masthead     brand, primary nav, social, search
  utility bar  secondary links and the date

Hand-copied into all 111 files, like the rest of the shared blocks, so the
deployed site still needs no build step. Idempotent.

Run:  python3 tools/magazine_chrome.py
"""
import glob, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

# Five headlines for the ticker — the pillar hubs, which are the pieces most
# worth sending a first-time reader to.
TICKER = [p for p in R.POSTS if p.get('kind') == 'hub'][:5]

ICONS = {
 'search': '<path d="M11.7 10.3a6 6 0 1 0-1.4 1.4l3.5 3.5 1.4-1.4-3.5-3.5zM7 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"/>',
 'rss':    '<path d="M3 3v2.5c5 0 9.5 4.5 9.5 9.5H15C15 8.4 9.6 3 3 3zm0 5v2.5c2.2 0 4 1.8 4 4H9.5C9.5 10.9 6.6 8 3 8zm1.5 5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/>',
 'mail':   '<path d="M2 4h14v10H2V4zm1.6 1.4L9 9.2l5.4-3.8H3.6zM3.5 7v5.6h11V7L9 10.8 3.5 7z"/>',
}


def icon(name, label, href='#'):
    return ('<a class="icon-btn" href="%s" aria-label="%s">'
            '<svg viewBox="0 0 18 18" aria-hidden="true">%s</svg></a>'
            % (href, label, ICONS[name]))


def chrome(depth):
    """The three bands, with every link resolved for this file's depth."""
    d = depth
    items = '\n'.join(
        '        <li><a href="%sposts/%s.html">%s</a></li>' % (d, p['slug'], p['title'])
        for p in TICKER)
    nav = [('categories/bodyweight-strength.html', 'Bodyweight'),
           ('categories/quick-workouts.html', 'Quick Workouts'),
           ('categories/small-space-training.html', 'Small Space'),
           ('categories/minimal-gear.html', 'Gear'),
           ('categories/habits-recovery.html', 'Habits'),
           ('about.html', 'About')]
    links = '\n'.join(
        '        <li><a class="nav__link" href="%s%s">%s</a></li>' % (d, h, t) for h, t in nav)
    mob = '\n'.join(
        '      <li><a class="mobile-nav__link" href="%s%s">%s</a></li>' % (d, h, t)
        for h, t in nav + [('contact.html', 'Contact')])
    return '''<!-- ===== SHARED HEADER — keep identical across all pages ===== -->
<div class="ticker">
  <div class="wrap ticker__inner">
    <span class="ticker__label">Latest <span>guides</span></span>
    <ul class="ticker__list">
%s
    </ul>
  </div>
</div>

<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="%sindex.html">
      <span class="brand__mark" aria-hidden="true"></span>
      <span class="brand__name">Health Wellness</span>
    </a>

    <nav class="nav" aria-label="Primary">
      <ul class="nav__list">
%s
      </ul>
    </nav>

    <div class="header-actions">
      <span class="header-actions__social">%s%s</span>
      %s
    </div>

    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>

  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile" hidden>
    <ul class="mobile-nav__list">
%s
    </ul>
  </nav>
</header>

<div class="utility-bar">
  <div class="wrap utility-bar__inner">
    <nav aria-label="Secondary">
      <ul>
        <li><a href="%scategories/quick-workouts.html">Start here</a></li>
        <li><a href="%sposts/4-week-home-workout-plan.html">The 4-week plan</a></li>
        <li><a href="%smedical-disclaimer.html">Medical disclaimer</a></li>
        <li><a href="%scontact.html">Contact</a></li>
      </ul>
    </nav>
    <span class="utility-bar__date" data-today>Updated weekly</span>
  </div>
</div>
<!-- ===== /SHARED HEADER ===== -->''' % (
        items, d, links,
        icon('rss', 'RSS feed', d + 'index.html'),
        icon('mail', 'Contact', d + 'contact.html'),
        icon('search', 'Search', d + 'index.html'),
        mob, d, d, d, d)


BLOCK = re.compile(
    r'<!-- ===== SHARED HEADER.*?<!-- ===== /SHARED HEADER ===== -->', re.S)

n = 0
for f in sorted(set(glob.glob('*.html') + glob.glob('posts/*.html')
                    + glob.glob('categories/*.html'))):
    depth = '../' if os.path.dirname(f) else ''
    src = io.open(f, encoding='utf-8').read()
    new = BLOCK.sub(lambda _: chrome(depth), src, count=1)
    if new != src:
        io.open(f, 'w', encoding='utf-8').write(new)
        n += 1
print('%d files given the magazine chrome' % n)
