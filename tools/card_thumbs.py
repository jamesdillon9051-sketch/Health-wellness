# -*- coding: utf-8 -*-
"""Give every category-page card a cover thumbnail.

The category listings were text-only, which reads as a blog index rather than a
magazine section front. Each card gets the post's text-free cover image above
its headline. The slug comes from the card's own link, so a card can never be
given the wrong picture. Idempotent.

Run:  python3 tools/card_thumbs.py
"""
import glob, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

CARD = re.compile(r'(<article class="card"[^>]*>)\s*(<div class="card__body">)', re.S)
LINK = re.compile(r'href="\.\./posts/([a-z0-9-]+)\.html"')

n = cards = 0
for f in sorted(glob.glob('categories/*.html')):
    src = io.open(f, encoding='utf-8').read()
    if 'card__media' in src:
        continue
    out, pos = [], 0
    for m in CARD.finditer(src):
        tail = src[m.end():m.end() + 600]
        link = LINK.search(tail)
        if not link:
            continue
        slug = link.group(1)
        if slug not in R.POST_BY_SLUG:
            continue
        media = ('\n        <a class="card__media" href="../posts/%s.html" tabindex="-1" aria-hidden="true">'
                 '\n          <img src="../assets/images/%s/%s-cover.jpg" alt="" '
                 'width="1200" height="900" loading="lazy">\n        </a>\n        ' % (slug, slug, slug))
        out.append(src[pos:m.end(1)] + media + m.group(2))
        pos = m.end()
        cards += 1
    if out:
        io.open(f, 'w', encoding='utf-8').write(''.join(out) + src[pos:])
        n += 1
print('%d category pages, %d cards given thumbnails' % (n, cards))
