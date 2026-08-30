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
ALL = {}
TAG = re.compile(r'<[^>]+>')

for f in sorted(glob.glob(os.path.join(R.ROOT, 'posts', '*.html'))):
    slug = os.path.basename(f)[:-5]
    if filt and filt not in slug:
        continue
    s = io.open(f, encoding='utf-8').read()
    srcs = dict((int(n), R._plain(t))
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
    ALL[slug] = hits
    print('\n=== %s ===' % slug)
    for n, claim, src in hits:
        print('  [%d] CLAIM : ...%s' % (n, claim))
        print('      SOURCE: %s' % src[:78])


# --- pairing heuristic -------------------------------------------------------
# Triage only: it flags claim/source pairs worth a human read, and it has both
# false positives and blind spots. It cannot tell you a citation is correct.
# Order does not matter: a claim is checked against the union of every rule it
# matches, so a claim about frequency at matched volume satisfies either source.
RULES = [
 (r'frequen(c|t)', ['Frequency']),
 (r'weekly (training )?volume|dose-response|more (hard )?sets per week', ['Dose-response']),
 (r'to failure|stopped short|proximity to failure|light(er)? loads?|low.load',
  ['Low- vs. High-Load', 'to Failure or Not', 'Bayesian']),
 (r'adult (activity )?guidance|two or more days a week|activity guidelines|WHO',
  ['World Health', 'NHS', 'Department of Health']),
 (r'sleep', ['Sleep Interventions']),
 (r'protein', ['protein']),
 (r'stretching', ['Stretching to prevent']),
 (r'foam rolling|self-myofascial', ['self-myofascial']),
 (r'cardiorespiratory fitness', ['high-intensity interval']),
 (r'talk test', ['Mayo']),
 (r'habit formation|automaticity|missed? (a single )?opportunit|66 days',
  ['How are habits formed']),
]


# --- apply the triage rules -------------------------------------------------
def expected(claim):
    """Union of every rule that matches, so rule order cannot cause a false flag.

    A claim mentioning both frequency and weekly volume is satisfied by either
    source; flagging it because one rule happened to be listed first was noise.
    """
    needles = []
    for pat, ns in RULES:
        if re.search(pat, claim, re.I):
            needles.extend(ns)
    return needles


flagged = []
for slug in sorted(ALL):
    for n, claim, src in ALL[slug]:
        if src.startswith('!!'):
            flagged.append((slug, n, claim, src, 'footnote resolves to nothing'))
            continue
        needles = expected(claim)
        if not needles:
            continue
        if not any(x.lower() in src.lower() for x in needles):
            flagged.append((slug, n, claim, src,
                            'expected one of: %s' % ', '.join(needles)))

print('\n' + '=' * 72)
print('TRIAGE — %d of %d footnotes flagged for a human read'
      % (len(flagged), sum(len(v) for v in ALL.values())))
print('=' * 72)
for slug, n, claim, src, why in flagged:
    print('\n%s  [%d]' % (slug, n))
    print('  CLAIM : ...%s' % claim)
    print('  SOURCE: %s' % src[:78])
    print('  WHY   : %s' % why)
if not flagged:
    print('\nNothing flagged. This is not proof the citations are correct —')
    print('the rules cover common claim types only. Read the pairs above.')
