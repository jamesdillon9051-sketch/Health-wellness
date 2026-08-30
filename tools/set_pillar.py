# -*- coding: utf-8 -*-
"""Apply the per-section template hooks to the built HTML. Idempotent.

  data-pillar  on every post and category <body> — picks one of the five
               section colours. Pages belonging to no pillar keep the house
               accent and get no attribute.
  data-hub     on the ten pillar hub posts, which get a heavier header than
               the clusters hanging off them.
  .cat-hero    wraps each category page's breadcrumb and header so the pillar
               colour can run edge to edge instead of sitting in a container.

Run:  python3 tools/set_pillar.py
"""
import glob, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

n = 0
for f in sorted(glob.glob('posts/*.html')) + sorted(glob.glob('categories/*.html')):
    if f.startswith('posts/'):
        meta = R.POST_BY_SLUG.get(os.path.basename(f)[:-5])
        if not meta:
            continue
        pillar = meta['pillar']
        hub = ' data-hub' if meta.get('kind') == 'hub' else ''
    else:
        pillar = os.path.basename(f)[:-5]
        hub = ''
    src = io.open(f, encoding='utf-8').read()
    new = re.sub(r'<body[^>]*>', '<body data-pillar="%s"%s>' % (pillar, hub), src, count=1)

    if f.startswith('categories/'):
        # lift the breadcrumb + header out of .wrap and into a full-bleed band
        new = new.replace(
            '<main id="main">\n  <div class="wrap">\n    <nav class="breadcrumb"',
            '<main id="main">\n  <div class="cat-hero">\n  <div class="wrap">\n    <nav class="breadcrumb"', 1)
        new = new.replace(
            '    </header>\n\n    <div class="ad-slot ad-slot--leaderboard"',
            '    </header>\n  </div>\n  </div>\n\n  <div class="wrap">\n    <div class="ad-slot ad-slot--leaderboard"', 1)
    if new != src:
        io.open(f, 'w', encoding='utf-8').write(new)
        n += 1
print('%d pages stamped with data-pillar' % n)
