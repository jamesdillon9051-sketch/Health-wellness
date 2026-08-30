# -*- coding: utf-8 -*-
"""Point alt text and figure captions at the photographs.

Two jobs:
  alt      the diagrams' alt text described line drawings that no longer exist.
           Each image now gets alt derived from the photograph's own title.
  credit   CC-BY images must name the photographer. The credit is appended to
           the figure caption and links to the licence.

Run:  python3 tools/photo_captions.py
"""
import glob, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

POOL = {p['file']: p for p in json.load(open('tools/photo-pool.json'))}
ASSIGN = json.load(open('tools/photo-assignments.json'))
NEEDS_CREDIT = {'by', 'by-sa', 'by-nc', 'by-nd'}


def clean_title(t):
    t = re.sub(r'\s*\(.*?\)\s*', ' ', t or '').strip(' .,-')
    t = re.sub(r'\s+', ' ', t)
    return t[:1].upper() + t[1:] if t else 'Photograph'


def alt_for(p):
    return clean_title(p.get('title')) + '.'


def credit_html(p):
    lic = (p.get('license') or '').lower()
    if lic not in NEEDS_CREDIT:
        return ''
    who = p.get('creator') or 'Unknown'
    name = 'CC %s %s' % (lic.upper(), p.get('license_version') or '')
    return (' <span class="credit">Photo: %s, <a href="%s" rel="nofollow noopener">%s</a>.</span>'
            % (who, p.get('license_url') or '#', name.strip()))


def main():
    alts = creds = 0
    for slug, fname in ASSIGN.items():
        p = POOL.get(fname)
        if not p:
            continue
        f = 'posts/%s.html' % slug
        if not os.path.exists(f):
            continue
        s = io.open(f, encoding='utf-8').read()
        orig = s

        # alt on every img pointing at this post's own artwork
        def swap(m):
            return re.sub(r'alt="[^"]*"', 'alt="%s"' % alt_for(p).replace('"', "'"),
                          m.group(0), count=1)
        s = re.sub(r'<img\b[^>]*?src="[^"]*%s-(?:hero|cover)\.jpg"[^>]*?>' % re.escape(slug),
                   swap, s, flags=re.S)

        # credit appended to the hero figcaption, once
        c = credit_html(p)
        if c and 'class="credit"' not in s:
            s = re.sub(r'(<figcaption>)(.*?)(</figcaption>)',
                       lambda m: m.group(1) + m.group(2) + c + m.group(3), s, count=1, flags=re.S)
            creds += 1
        if s != orig:
            io.open(f, 'w', encoding='utf-8').write(s)
            alts += 1
    print('%d posts updated, %d credits added' % (alts, creds))


if __name__ == '__main__':
    main()
