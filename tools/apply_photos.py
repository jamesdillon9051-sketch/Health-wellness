# -*- coding: utf-8 -*-
"""Assign pool photographs to posts, crop them, and write the credits page.

Openverse returns mostly CC-BY and CC-BY-SA, which REQUIRE attribution. That is
not optional and not something to remember by hand, so every image carries its
creator and licence through from photo-pool.json into credits.html and into a
caption under the picture.

Run:  python3 tools/apply_photos.py
"""
import json, os, re, sys, io as _io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from PIL import Image, ImageOps

POOL = json.load(open('tools/photo-pool.json'))
BY_KEY = {}
for p in POOL:
    BY_KEY.setdefault(p['key'], []).append(p)

# Which pool category suits which kind of post. Checked in order, first match
# wins, so the specific patterns come before the general ones.
RULES = [
 (r'sleep|recovery|rest|deload|tired|doms|soreness|foam-rolling',  ['sleep', 'foam-roller', 'bedroom']),
 (r'protein|nutrition|meal|eat|weight-loss|high-protein',          ['protein-food', 'breakfast']),
 (r'stair|step',                                                   ['stairs-home', 'walking']),
 (r'run|cardio|hiit|jump-rope|jump|walk',                          ['running-shoes', 'park-run', 'jump-rope', 'walking']),
 (r'band|loop-band|tube-band',                                     ['resistance-band', 'dumbbell-pair']),
 (r'kettlebell',                                                   ['kettlebell', 'dumbbell-pair']),
 (r'dumbbell|weighted-vest|bench|adjustable',                      ['dumbbell-pair', 'home-dumbbell']),
 (r'mat|carpet|floor|yoga',                                        ['gym-mat', 'home-mat', 'yoga-pose', 'home-yoga']),
 (r'pull-up|doorway|rings|suspension',                             ['pull-up-bar', 'home-exercise']),
 (r'stretch|mobility|warm-up|cool-down|desk|posture',              ['stretch', 'home-yoga', 'yoga-pose']),
 (r'morning|evening|shift',                                        ['window-light', 'clock', 'coffee']),
 (r'apartment|small-space|studio|quiet|noise|ceiling|bedroom|space|balcony',
                                                                   ['living-room', 'bedroom', 'home-mat']),
 (r'app|gear|equipment|gym|storage|buy|cheap|under-100|diy|slider|vest',
                                                                   ['dumbbell-pair', 'gym-mat', 'home-dumbbell']),
 (r'travel|hotel|office|lunch',                                    ['home-exercise', 'living-room']),
 (r'kids|parent|family',                                           ['home-exercise', 'living-room']),
 (r'push|chest|arm|shoulder|dip',                                  ['press-up', 'home-exercise']),
 (r'plank|core|ab|situp',                                          ['plank', 'home-mat', 'home-exercise']),
 (r'squat|leg|glute|lunge|calf|pistol|bulgarian',                  ['squat-home', 'lunge', 'home-exercise']),
 # Last, so an exercise name never loses to a substring like the
 # 'progress' inside 'plank-progression'.
 (r'habit|motivation|consistency|stick-to|restart|drop-off|tracking|'
 r'schedule|weekly|routine|how-many-days|split|structure',
                                                                   ['notebook', 'calendar', 'clock']),
]
DEFAULT = ['home-exercise', 'home-mat', 'home-yoga', 'yoga-pose', 'home-dumbbell', 'living-room']


def pick(slug, used):
    """Choose a photo for this post.

    Topical fit outranks spreading: an unused generic photo must not beat a
    once-used photo of the actual subject, or the scheduling posts end up
    illustrated with yoga. Rule keys are tried in order and DEFAULT only when
    they are empty; usage count breaks ties *within* a preference tier.
    """
    keys = DEFAULT
    for pat, ks in RULES:
        if re.search(pat, slug):
            keys = ks + [k for k in DEFAULT if k not in ks]
            break
    ranked = []
    for tier, k in enumerate(keys):
        for p in BY_KEY.get(k, []):
            n = used.get(p['file'], 0)
            # Past three uses a photo drops a tier, so no single picture ends up
            # on seven pages just because it matched the rule best.
            ranked.append((tier + (2 if n >= 3 else 0), n,
                           -(p['width'] * p['height']), p))
    if not ranked:
        ranked = [(0, used.get(p['file'], 0), 0, p) for p in POOL]
    ranked.sort(key=lambda r: r[:3])
    return ranked[0][3] if ranked else None


def crop(src, dst, w, h):
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert('RGB')
    im = ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.4))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, 'JPEG', quality=82, optimize=True, progressive=True)


NEEDS_CREDIT = {'by', 'by-sa', 'by-nd', 'by-nc'}


def credit_line(p):
    who = p.get('creator') or 'Unknown'
    lic = (p.get('license') or '').upper()
    ver = p.get('license_version') or ''
    return '%s — CC %s %s' % (who, lic, ver).strip()


def main():
    used, assigned = {}, {}
    for post in R.POSTS:
        slug = post['slug']
        p = pick(slug, used)
        if not p:
            continue
        used[p['file']] = used.get(p['file'], 0) + 1
        assigned[slug] = p
        src = os.path.join('tools/photos', p['file'])
        crop(src, 'assets/images/%s/%s-hero.jpg' % (slug, slug), 1200, 630)
        crop(src, 'assets/images/%s/%s-cover.jpg' % (slug, slug), 1200, 900)
    json.dump({k: v['file'] for k, v in assigned.items()},
              open('tools/photo-assignments.json', 'w'), indent=1)
    print('%d posts given photographs, %d distinct images used'
          % (len(assigned), len(used)))
    print('most reused: %s' % sorted(used.items(), key=lambda x: -x[1])[:3])
    return assigned


if __name__ == '__main__':
    main()
