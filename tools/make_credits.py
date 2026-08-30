# -*- coding: utf-8 -*-
"""Generate credits.html from the photo pool.

CC-BY and CC-BY-SA REQUIRE attribution. That is a licence condition, not a
courtesy, so the credit is generated from the same record the image came from
rather than written by hand and hoped to stay accurate.

Run:  python3 tools/make_credits.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

POOL = {p['file']: p for p in json.load(open('tools/photo-pool.json'))}

# Credit whatever is actually assigned to a post; before the first assignment
# run, credit the whole pool so the page is never a dead link in the footer.
try:
    ASSIGN = json.load(open('tools/photo-assignments.json'))
except (IOError, ValueError):
    ASSIGN = {p['file']: p['file'] for p in POOL.values()}

LICENCE_NAME = {
    'cc0': 'CC0 1.0 (public domain dedication)',
    'pdm': 'Public Domain Mark',
    'public-domain': 'Public domain',
    'by': 'CC BY', 'by-sa': 'CC BY-SA', 'by-nc': 'CC BY-NC', 'by-nd': 'CC BY-ND',
}


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rows():
    seen, out = set(), []
    for slug in sorted(ASSIGN):
        f = ASSIGN[slug]
        p = POOL.get(f)
        if not p or f in seen:
            continue
        seen.add(f)
        lic = (p.get('license') or '').lower()
        if lic in LICENCE_NAME:
            name = LICENCE_NAME[lic]
        else:
            bits = lic.split('-')                     # 'by-sa-4.0' -> CC BY-SA 4.0
            ver = bits[-1] if bits and bits[-1][:1].isdigit() else ''
            fam = '-'.join(b for b in bits if b != ver).upper()
            name = ('CC %s %s' % (fam, ver)).strip()
        out.append((p.get('title') or f, p.get('creator') or 'Unknown',
                    p.get('creator_url') or '', name, p.get('license_url') or '',
                    p.get('landing') or '', p.get('source') or ''))
    return out


def main():
    body = []
    for title, who, who_url, lic, lic_url, landing, source in rows():
        creator = ('<a href="%s" rel="nofollow noopener">%s</a>' % (esc(who_url), esc(who))
                   if who_url else esc(who))
        body.append(
            '        <tr>\n'
            '          <td><a href="%s" rel="nofollow noopener">%s</a></td>\n'
            '          <td>%s</td>\n'
            '          <td><a href="%s" rel="nofollow noopener">%s</a></td>\n'
            '          <td>%s</td>\n'
            '        </tr>' % (esc(landing), esc(title), creator,
                               esc(lic_url), esc(lic), esc(source)))
    print('\n'.join(body))
    print('\n%d distinct images credited' % len(rows()), file=sys.stderr)


if __name__ == '__main__':
    main()
