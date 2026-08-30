# -*- coding: utf-8 -*-
"""Drop pool images that are wrong for this site, and say why.

The title filters in the fetchers catch obvious junk, but a lot slipped past on
titles that name nothing: US Department of Defense photos are filed under IDs
like '160812-M-EU132-379', so 'army' and 'soldier' never matched. Military PT,
commercial-gym coaching and competition powerlifting are all the opposite of
what this site is about — training alone, at home, with nothing.

Run:  python3 tools/prune_pool.py         # report only
      python3 tools/prune_pool.py --apply # rewrite photo-pool.json
"""
import json, re, sys

POOL = 'tools/photo-pool.json'

# DoD photo IDs: YYMMDD-BRANCH-UNIT-SEQ, e.g. 160812-M-EU132-379
DOD_ID = re.compile(r'^\d{6}-[a-z]-[a-z0-9]{4,6}-\d', re.I)

REJECT = [
 ('military',    r'\b(u\.?s\.?\s*(army|navy|marine|air force)|sgt|sergeant|corporal|'
                 r'marine corps|naval|soldier|airman|platoon|barracks|deployment|'
                 r'mediterranean sea|south china sea|arabian gulf|camp \w+)\b'),
 ('conflict',    r'славянск|donbas|kyiv|kharkiv|checkpoint'),
 ('commercial',  r'\b(coach|athlete|instructor|dj |aquatics|crossfit|gymnasium|'
                 r'personal train|studio session)\b'),
 ('competition', r'\b(competition|championship|u1[0-9] |elite|meet\b|tournament|league)\b'),
 ('barbell-gym', r'\b(barbell|deadlift|squat rack|weightlifting|powerlifting|bench press)\b'),
 ('not-fitness', r'\b(test rig|чехол|tenerife 2023)\b'),
 ('historical',  r'\b(18\d\d|19[0-2]\d)\b'),
]


def reason(title):
    t = (title or '').strip()
    if DOD_ID.match(t):
        return 'military (DoD photo ID)'
    low = t.lower()
    for name, pat in REJECT:
        if re.search(pat, low):
            return name
    return None


def main():
    pool = json.load(open(POOL))
    keep, drop = [], []
    for p in pool:
        r = reason(p.get('title'))
        (drop if r else keep).append((p, r))
    print('pool %d -> keep %d, drop %d\n' % (len(pool), len(keep), len(drop)))
    for p, r in drop:
        print('  %-22s %-16s %s' % (r, p.get('key'), (p.get('title') or '')[:52]))
    if '--apply' in sys.argv:
        json.dump([p for p, _ in keep], open(POOL, 'w'), indent=1)
        print('\nwritten: %d images remain' % len(keep))


if __name__ == '__main__':
    main()
