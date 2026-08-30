# -*- coding: utf-8 -*-
"""Generate sitemap.xml, robots.txt and image-briefs.md from the built site."""
import sys, os, re, io, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from excerpts import EXCERPTS

TODAY = '2026-08-29'

# ------------------------------------------------------------------ sitemap
urls = []
def add(path, pri, freq):
    urls.append((path, pri, freq))

add('', '1.0', 'weekly')
for pl in R.PILLARS:
    add('categories/%s.html' % pl['key'], '0.9', 'weekly')
for p in R.POSTS:
    add('posts/%s.html' % p['slug'], '0.8' if p['kind'] == 'hub' else '0.7', 'monthly')
for page in ['about.html', 'contact.html', 'privacy-policy.html', 'medical-disclaimer.html',
             'credits.html']:
    add(page, '0.5', 'yearly')

body = '\n'.join(
    '  <url>\n    <loc>%s/%s</loc>\n    <lastmod>%s</lastmod>\n'
    '    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>'
    % (R.DOMAIN, path, TODAY, freq, pri) for path, pri, freq in urls)

R.write('sitemap.xml',
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % body)

# ------------------------------------------------------------------ robots
R.write('robots.txt', """# robots.txt for %s
User-agent: *
Allow: /

# No crawlable value in these
Disallow: /tools/
Disallow: /404.html

Sitemap: %s/sitemap.xml
""" % (R.SITE, R.DOMAIN))

# ------------------------------------------------------- image briefs index
BRIEF = re.compile(
    r'<!--\s*IMAGE BRIEF:\s*(?P<file>[\w\-.]+)\s*\((?P<dims>[^)]+)\)(?P<body>.*?)-->',
    re.S)

rows = []
for f in sorted(glob.glob('posts/*.html')) + ['index.html']:
    slug = os.path.basename(f)[:-5]
    src = io.open(f, encoding='utf-8').read()
    for m in BRIEF.finditer(src):
        detail = re.sub(r'\s+', ' ', m.group('body')).strip()
        rows.append((slug, m.group('file'), m.group('dims'), detail))

by_post = {}
for slug, fn, dims, detail in rows:
    by_post.setdefault(slug, []).append((fn, dims, detail))

lines = ["""# Image Briefs — %s

Every image the site needs, in one checklist. Generated from the `IMAGE BRIEF`
comments in the HTML, so this file and the pages cannot drift apart — regenerate
with `python3 tools/build_site_files.py` after adding or editing a brief.

**Where files go:** `assets/images/<post-slug>/<filename>`

**Naming:** `<post-slug>-hero.jpg` for the hero (1200x630, also the Open Graph
share image), then `<post-slug>-01.jpg`, `-02.jpg` and so on for in-content images.

**Palette to match** — cool drafting ground `#E9EDF1`, navy `#22384A`,
cobalt `#2B4EC7`, surveyor's yellow `#F5D547` used sparingly.

**Total images needed: %d unique files** across %d pages. (The homepage reuses
ten post heroes, so there are more `<img>` tags than files to source.)

**Photographs are already in place — nothing here is outstanding.** Every path
below holds a real photograph, sourced from [Openverse](https://openverse.org/)
and Wikimedia Commons under licences that permit commercial use and
modification, then cropped to size.

**Attribution matters.** Some images are CC-BY or CC-BY-SA, which require naming
the photographer — a licence condition, not a courtesy. `credits.html` lists
every image, its photographer and its licence, and is generated from the same
manifest the images came from. Re-run `python3 tools/build_credits_page.py` if
you change any image.

The briefs below describe the photography originally specified. They are kept as
a reference for what each post ideally wants; if you commission or buy a better
picture, overwrite the file at the same path and update the alt text.
`tools/make_images.py` still exists and will redraw the diagram versions if you
ever want them back.

---
""" % (R.SITE, len(set(r[1] for r in rows)), len(by_post))]

for slug in sorted(by_post):
    meta = R.POST_BY_SLUG.get(slug)
    title = meta['title'] if meta else 'Homepage'
    lines.append('\n## %s\n' % title)
    if meta:
        lines.append('`posts/%s.html` — folder: `assets/images/%s/`\n' % (slug, slug))
    else:
        lines.append('`index.html` — images live in each post\'s own folder\n')
    for fn, dims, detail in by_post[slug]:
        lines.append('\n- [ ] **`%s`** (%s)\n      %s\n' % (fn, dims, detail))

R.write('image-briefs.md', ''.join(lines))
print('sitemap.xml : %d URLs' % len(urls))
print('robots.txt  : written')
print('image-briefs: %d unique images across %d pages' % (len(set(r[1] for r in rows)), len(by_post)))
