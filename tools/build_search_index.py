# -*- coding: utf-8 -*-
"""Build the client-side search index.

The site is static, so search runs in the browser against a prebuilt index.
Full body text would be about 340,000 words — several megabytes, far too much
to ship. Indexing the title, standfirst, section headings and target keyword
covers what people actually type ("push up", "small flat", "protein") at a
fraction of the size.

Run:  python3 tools/build_search_index.py
"""
import glob, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

TAG = re.compile(r'<[^>]+>')
LABEL = {'bodyweight-strength': 'Bodyweight', 'quick-workouts': 'Quick workouts',
         'small-space-training': 'Small space', 'minimal-gear': 'Gear',
         'habits-recovery': 'Habits'}
SKIP_HEADING = ("what's in this guide", 'sources', 'frequently asked questions',
                'about the author', 'related')


def plain(frag):
    import html as _h
    return re.sub(r'\s+', ' ', _h.unescape(TAG.sub(' ', frag or ''))).strip()


def main():
    out = []
    for f in sorted(glob.glob('posts/*.html')):
        slug = os.path.basename(f)[:-5]
        meta = R.POST_BY_SLUG.get(slug)
        if not meta:
            continue
        s = io.open(f, encoding='utf-8').read()
        lede = re.search(r'<p class="lede">(.*?)</p>', s, re.S)
        heads = []
        for h in re.findall(r'<h[23][^>]*>(.*?)</h[23]>', s, re.S):
            t = plain(h)
            if t and not t.lower().startswith(SKIP_HEADING):
                heads.append(t)
        words = len(plain(re.split(r'<section class="sources"', s)[0]).split())
        out.append({
            's': slug,
            't': meta['title'],
            'd': plain(lede.group(1)) if lede else '',
            'c': LABEL.get(meta['pillar'], meta['pillar']),
            'p': meta['pillar'],
            'k': meta.get('keyword', ''),
            'h': heads[:10],
            'w': words,
            'g': meta.get('kind') == 'hub',
        })
    dst = 'assets/search-index.json'
    io.open(dst, 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    kb = os.path.getsize(dst) / 1024.0
    print('%s: %d posts, %.0f KB' % (dst, len(out), kb))


if __name__ == '__main__':
    main()
