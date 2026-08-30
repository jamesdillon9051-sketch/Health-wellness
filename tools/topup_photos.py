# -*- coding: utf-8 -*-
"""Top up the thin categories and MERGE into the existing pool.

The broad sweep skewed towards food and sleep imagery, because those words are
unambiguous in English. Photographs of people actually training at home are the
site's core subject and came back thinnest, so they get their own pass with many
phrasings of the same idea.

Run:  python3 tools/topup_photos.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_photos as F

EXTRA = [
 ('home-exercise', 'woman exercising at home fitness'),
 ('home-exercise', 'home fitness training indoor exercise'),
 ('home-exercise', 'exercising indoors bodyweight training'),
 ('home-exercise', 'fitness workout indoors woman'),
 ('home-exercise', 'man doing exercise indoors fitness'),
 ('home-mat',      'exercise on yoga mat indoor'),
 ('home-mat',      'fitness mat floor exercise home'),
 ('home-yoga',     'yoga at home indoor practice'),
 ('home-yoga',     'yoga stretching indoor mat'),
 ('yoga-pose',     'yoga asana pose practice'),
 ('stretch',       'stretching exercise indoor fitness'),
 ('press-up',      'push ups exercise fitness training'),
 ('plank',         'plank exercise abs core training'),
 ('squat-home',    'squat exercise fitness training'),
 ('lunge',         'lunges exercise fitness training'),
 ('gym-mat',       'yoga mat equipment fitness'),
 ('resistance-band','exercise band elastic fitness training'),
 ('pull-up-bar',   'pull ups bar exercise fitness'),
 ('dumbbell-pair', 'dumbbell weights gym equipment'),
 ('foam-roller',   'foam roller stretching recovery'),
 ('living-room',   'living room sofa apartment interior'),
 ('window-light',  'window light room interior morning'),
 ('clock',         'clock time alarm morning'),
 ('calendar',      'calendar planner month schedule'),
 ('towel',         'towel folded clean textile'),
]

pool = json.load(open(F.POOL))
have_url = {p.get('landing') for p in pool}
have_title = {(p.get('title') or '').lower() for p in pool}
added = 0

for key, term in EXTRA:
    hits = F.search(term, 20, 1) + F.search(term, 20, 2)
    kept = 0
    for h in hits:
        title = (h.get('title') or '').lower()
        if any(j in title for j in F.JUNK) or title in have_title:
            continue
        if h.get('foreign_landing_url') in have_url:
            continue
        w, hh = h.get('width') or 0, h.get('height') or 0
        if w < F.MIN_W or hh < F.MIN_H or not h.get('url'):
            continue
        import hashlib
        name = '%s-%s.jpg' % (key, hashlib.md5(h['url'].encode()).hexdigest()[:8])
        path = os.path.join(F.OUT, name)
        if not os.path.exists(path):
            data = F.fetch(F.thumb_url(h['url']))
            import time; time.sleep(F.PAUSE)
            if not data or len(data) < 25000:
                continue
            open(path, 'wb').write(data)
        have_title.add(title); have_url.add(h.get('foreign_landing_url'))
        pool.append({'key': key, 'query': term, 'file': name,
                     'title': h.get('title'), 'creator': h.get('creator'),
                     'creator_url': h.get('creator_url'), 'license': h.get('license'),
                     'license_version': h.get('license_version'),
                     'license_url': h.get('license_url'), 'source': h.get('source'),
                     'landing': h.get('foreign_landing_url'), 'width': w, 'height': hh})
        kept += 1; added += 1
        if kept >= 4:
            break
    print('%-16s +%d' % (key, kept))

json.dump(pool, open(F.POOL, 'w'), indent=1)
print('\nadded %d, pool now %d images' % (added, len(pool)))
