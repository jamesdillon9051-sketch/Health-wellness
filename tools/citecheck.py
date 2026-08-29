# -*- coding: utf-8 -*-
"""
Print every footnoted claim next to the source it points at, so the pairing can
be eyeballed. Automated checks can confirm a footnote resolves; only a human
read confirms it supports the claim.

    python3 tools/citecheck.py [slug-substring]
"""
import sys, os, re, io, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

filt = sys.argv[1] if len(sys.argv) > 1 else ''
TAG = re.compile(r'<[^>]+>')

for f in sorted(glob.glob(os.path.join(R.ROOT, 'posts', '*.html'))):
    slug = os.path.basename(f)[:-5]
    if filt and filt not in slug:
        continue
    s = io.open(f, encoding='utf-8').read()
    srcs = dict((int(n), R._plain(t)[:78])
                for n, t in re.findall(r'<li id="source-(\d+)">(.*?)</li>', s, re.S))
    body = s.split('<section class="sources"')[0]
    hits = []
    for m in re.finditer(r'<sup><a href="#source-(\d+)">', body):
        n = int(m.group(1))
        start = max(0, m.start() - 320)
        claim = R._plain(body[start:m.start()])
        claim = claim.split('. ')[-1][-160:]
        hits.append((n, claim, srcs.get(n, '!! MISSING')))
    if not hits:
        continue
    print('\n=== %s ===' % slug)
    for n, claim, src in hits:
        print('  [%d] CLAIM : ...%s' % (n, claim))
        print('      SOURCE: %s' % src)


# --- pairing heuristic -------------------------------------------------------
# Order matters: the frequency rule must be tested before the volume rule,
# because frequency claims almost always mention volume being held equal.
RULES = [
 (r'frequenc', ['Frequency']),
 (r'weekly (training )?volume|dose-response|more (hard )?sets per week', ['Dose-response']),
 (r'sets taken to failure|stopped short|absolute failure',
  ['to Failure or Not', 'Low- vs. High-Load']),
 (r'close to failure|proximity to failure|light(er)? loads?|low.load',
  ['Low- vs. High-Load', 'to Failure or Not', 'Bayesian']),
 (r'adult (activity )?guidance|two or more days a week|activity guidelines',
  ['World Health', 'NHS', 'Department of Health']),
 (r'sleep', ['Sleep Interventions']),
 (r'protein', ['protein']),
 (r'stretching', ['Stretching to prevent']),
 (r'foam rolling|self-myofascial', ['self-myofascial']),
 (r'cardiorespiratory fitness', ['high-intensity interval']),
 (r'talk test', ['Mayo']),
]
