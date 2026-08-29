# -*- coding: utf-8 -*-
"""
Site audit. Run after writing or editing posts:

    python3 tools/audit.py          # report only
    python3 tools/audit.py --fix    # also resync wordCount in the JSON-LD

Checks every post for word count, internal links, external links, valid
JSON-LD, image briefs and required SEO tags.
"""
import sys, os, re, io, glob, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

FIX = '--fix' in sys.argv
ROOT = R.ROOT
MIN_CLUSTER, MIN_HUB = 1200, 2500

def prose_of(s):
    m = re.search(r'<div class="prose">(.*?)<section class="sources"', s, re.S)
    return m.group(1) if m else ''

def main():
    problems, rows = [], []
    files = sorted(glob.glob(os.path.join(ROOT, 'posts', '*.html')))

    for f in files:
        slug = os.path.basename(f)[:-5]
        s = io.open(f, encoding='utf-8').read()
        meta = R.POST_BY_SLUG.get(slug)
        if not meta:
            problems.append('%s: not in content-map.md' % slug); continue

        prose = prose_of(s)
        words = len(R._plain(prose).split())
        floor = MIN_HUB if meta['kind'] == 'hub' else MIN_CLUSTER

        internal = len(set(re.findall(r'href="((?!http)(?:\.\./)?[a-z0-9\-/]+\.html)"', prose)))
        external = len(set(re.findall(r'href="(https?://[^"]+)"', s)))
        briefs = len(re.findall(r'IMAGE BRIEF', s))

        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
        types = []
        for b in blocks:
            try:
                types.append(json.loads(b).get('@type'))
            except ValueError as e:
                problems.append('%s: invalid JSON-LD (%s)' % (slug, e))

        if FIX:
            s2 = re.sub(r'"wordCount": \d+', '"wordCount": %d' % words, s, count=1)
            if s2 != s:
                io.open(f, 'w', encoding='utf-8').write(s2)

        if words < floor:
            problems.append('%s: %d words, below the %d floor for a %s post'
                            % (slug, words, floor, meta['kind']))
        if internal < 3:
            problems.append('%s: only %d internal links (3 required)' % (slug, internal))
        if external < 1:
            problems.append('%s: no external authority links' % slug)
        if 'Article' not in types:
            problems.append('%s: missing Article schema' % slug)
        if 'BreadcrumbList' not in types:
            problems.append('%s: missing BreadcrumbList schema' % slug)
        if briefs < 1:
            problems.append('%s: no image brief' % slug)
        for tag in ('rel="canonical"', 'og:title', 'twitter:card', 'name="description"'):
            if tag not in s:
                problems.append('%s: missing %s' % (slug, tag))

        rows.append((slug, meta['kind'], words, internal, external, briefs, len(blocks)))

    print('%-42s %-8s %6s %4s %4s %4s %4s' % ('POST', 'TYPE', 'WORDS', 'INT', 'EXT', 'IMG', 'LD'))
    for r in rows:
        print('%-42s %-8s %6d %4d %4d %4d %4d' % r)

    print('\n%d of 100 posts written.' % len(rows))
    if rows:
        print('Average words: %d' % (sum(r[2] for r in rows) // len(rows)))
    if problems:
        print('\n%d problem(s):' % len(problems))
        for p in problems:
            print('  - ' + p)
        return 1
    print('\nNo problems found.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
