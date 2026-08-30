# -*- coding: utf-8 -*-
"""Mine Wikimedia Commons categories for exercise photography.

Openverse matches on titles, which is why a search for "squat" returned squat
lobsters. Commons categories are curated by people, so Category:Push-ups
actually contains push-ups. That makes it the better source for the specific
exercise imagery this site needs.

Licences are read per file from imageinfo extmetadata rather than assumed —
Commons carries everything from CC0 to CC-BY-SA to non-free logos, and only the
free ones are kept.

Run:  python3 tools/commons_photos.py
"""
import json, os, re, time, urllib.parse, urllib.request, hashlib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_photos as F

API = 'https://commons.wikimedia.org/w/api.php'
PAUSE = 1.1
MIN_W, MIN_H = 1200, 800

# Licences that permit commercial use and modification. Anything else is
# dropped, including the NC and ND variants.
OK_LICENCE = re.compile(r'^(cc0|cc-by(-sa)?([-\d.]*)?$|cc-by(-sa)?-[\d.]+|public-domain|pd(-|$))')


def norm_licence(v):
    """Commons reports 'CC BY-SA 4.0'; normalise to 'cc-by-sa-4.0' before
    matching. Matching the raw string silently rejected every CC-BY-SA file,
    which is why the first Commons run added nothing at all."""
    return re.sub(r'[\s_]+', '-', (v or '').strip().lower())


def licence_ok(v):
    n = norm_licence(v)
    parts = n.split('-')
    if 'nc' in parts or 'nd' in parts:
        return False              # non-commercial / no-derivatives
    return bool(n) and bool(OK_LICENCE.match(n))

CATEGORIES = [
 ('press-up',        'Push-ups'),
 ('plank',           'Plank (exercise)'),
 ('squat-home',      'Squat (exercise)'),
 ('lunge',           'Lunge (exercise)'),
 ('home-exercise',   'Physical exercise'),
 ('home-exercise',   'Exercising women'),
 ('home-exercise',   'Exercising men'),
 ('stretch',         'Stretching'),
 ('home-yoga',       'Yoga'),
 ('gym-mat',         'Yoga mats'),
 ('dumbbell-pair',   'Dumbbells'),
 ('kettlebell',      'Kettlebells'),
 ('resistance-band', 'Resistance bands'),
 ('pull-up-bar',     'Pull-ups'),
 ('jump-rope',       'Skipping ropes'),
 ('foam-roller',     'Foam rollers'),
]

# Commons is full of military PT, competition sport and medical diagrams; none
# of it suits a blog about training in a small flat.
JUNK = F.JUNK + ('army', 'soldier', 'marine', 'navy', 'air force', 'military',
                 'regiment', 'cadet', 'academy', 'competition', 'championship',
                 'world cup', 'olympic', 'crossfit games', 'anatomy', 'muscle diagram',
                 'svg', '.png', 'plaque', 'sign', 'logo')


def api(params):
    u = API + '?' + urllib.parse.urlencode(dict(params, format='json'))
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(u, headers=F.UA), timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(5 * (i + 1)); continue
            return {}
        except Exception:
            return {}
    return {}


def files_in(cat, n=40):
    r = api({'action': 'query', 'list': 'categorymembers',
             'cmtitle': 'Category:' + cat, 'cmtype': 'file', 'cmlimit': n})
    return [m['title'] for m in r.get('query', {}).get('categorymembers', [])]


def info(titles):
    r = api({'action': 'query', 'titles': '|'.join(titles), 'prop': 'imageinfo',
             'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1800})
    out = []
    for page in (r.get('query', {}).get('pages') or {}).values():
        ii = (page.get('imageinfo') or [{}])[0]
        meta = ii.get('extmetadata') or {}
        out.append({
            'title': page.get('title', '').replace('File:', ''),
            'url': ii.get('thumburl') or ii.get('url'),
            'width': ii.get('width') or 0, 'height': ii.get('height') or 0,
            'licence': (meta.get('LicenseShortName', {}) or {}).get('value', ''),
            'licence_url': (meta.get('LicenseUrl', {}) or {}).get('value', ''),
            'artist': re.sub(r'<[^>]+>', '', (meta.get('Artist', {}) or {}).get('value', '') or '').strip(),
            'landing': ii.get('descriptionurl') or '',
        })
    return out


def main():
    pool = json.load(open(F.POOL))
    have = {(p.get('title') or '').lower() for p in pool}
    added = 0
    for key, cat in CATEGORIES:
        titles = files_in(cat)
        time.sleep(PAUSE)
        kept = 0
        for chunk in [titles[i:i + 12] for i in range(0, len(titles), 12)]:
            if kept >= 5:
                break
            for m in info(chunk):
                if kept >= 5:
                    break
                t = (m['title'] or '').lower()
                if not m['url'] or not t.endswith(('.jpg', '.jpeg')):
                    continue
                if any(j in t for j in JUNK) or t in have:
                    continue
                if m['width'] < MIN_W or m['height'] < MIN_H:
                    continue
                if not licence_ok(m['licence']):
                    continue
                name = '%s-c%s.jpg' % (key, hashlib.md5(m['url'].encode()).hexdigest()[:8])
                path = os.path.join(F.OUT, name)
                if not os.path.exists(path):
                    data = F.fetch(m['url'])
                    time.sleep(PAUSE)
                    if not data or len(data) < 25000:
                        continue
                    open(path, 'wb').write(data)
                lic = norm_licence(m['licence']).replace('cc-', '', 1)
                have.add(t)
                pool.append({'key': key, 'query': 'Commons: ' + cat, 'file': name,
                             'title': m['title'].rsplit('.', 1)[0].replace('_', ' '),
                             'creator': m['artist'][:90] or 'Unknown',
                             'creator_url': '', 'license': lic,
                             'license_version': '', 'license_url': m['licence_url'],
                             'source': 'wikimedia', 'landing': m['landing'],
                             'width': m['width'], 'height': m['height']})
                kept += 1; added += 1
            time.sleep(PAUSE)
        print('%-16s %-24s +%d' % (key, cat, kept))
    json.dump(pool, open(F.POOL, 'w'), indent=1)
    print('\nadded %d from Commons; pool now %d' % (added, len(pool)))


if __name__ == '__main__':
    main()
