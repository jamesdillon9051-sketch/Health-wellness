# -*- coding: utf-8 -*-
"""Search Openverse for freely-licensed photography and build a vetted pool.

Openverse keyword-matches titles, so short queries fail badly: "squat" returns
squat lobsters, "push up" returns starfish. Every query here is long and
specific for that reason.

Licences: CC0 and PDM need no attribution; CC-BY and CC-BY-SA do. Everything
downloaded is recorded in photo-pool.json with its licence, creator and source
URL so credit can be generated rather than remembered.

Run:  python3 tools/fetch_photos.py            # search + download the pool
"""
import json, os, re, time, urllib.parse, urllib.request, hashlib, sys

# Wikimedia asks for a descriptive User-Agent and polite request rates. The
# first run of this script was rate-limited (HTTP 429) for hammering
# upload.wikimedia.org with full-size originals, several megabytes each.
UA = {'User-Agent': 'HealthWellnessSiteBuilder/1.0 (static site image sourcing; '
                    'contact via repository issues)'}
PAUSE = 1.2          # seconds between downloads
THUMB_W = 1800       # ask for a sized thumbnail, not the original
OUT = 'tools/photos'
POOL = 'tools/photo-pool.json'
MIN_W, MIN_H = 1300, 900

# (key, query). The key is what posts are matched against later.
QUERIES = [
 # People training at home — the site's actual subject. These queries return
 # the strongest results, so several angles on the same idea are worth having.
 ('home-exercise',   'woman exercises at home using a fitness mat'),
 ('home-exercise',   'workout session at home with a woman exercising'),
 ('home-exercise',   'man exercising at home living room'),
 ('home-exercise',   'people exercising at home indoor workout'),
 ('home-dumbbell',   'woman exercising with a dumbbell at home'),
 ('home-dumbbell',   'woman stretching on a mat with dumbbells'),
 ('home-mat',        'woman doing exercise at home on a mat'),
 ('home-mat',        'exercise mat floor workout indoor'),
 ('home-yoga',       'woman practicing yoga at home on a mat'),
 ('home-yoga',       'yoga practice indoor living room'),
 ('yoga-pose',       'yoga pose stretching indoor'),
 ('press-up',        'press up exercise floor'),
 ('press-up',        'man doing push ups on the floor'),
 ('plank',           'plank position core exercise'),
 ('lunge',           'lunge exercise legs indoor'),
 ('squat-home',      'bodyweight squat exercise indoor'),
 ('stretch',         'stretching exercise flexibility indoor'),
 ('stretch',         'woman stretching legs floor'),
 # Equipment
 ('dumbbell-pair',   'dumbbells on the floor fitness weights'),
 ('dumbbell-pair',   'hand weights dumbbell pair'),
 ('kettlebell',      'kettlebell weight training equipment'),
 ('resistance-band', 'resistance bands exercise equipment'),
 ('resistance-band', 'running shoes hand weights and resistance bands'),
 ('gym-mat',         'rolled yoga mat exercise equipment'),
 ('jump-rope',       'jump rope skipping rope fitness'),
 ('pull-up-bar',     'pull up bar horizontal bar exercise'),
 ('foam-roller',     'foam roller muscle recovery'),
 ('water-bottle',    'water bottle sports hydration'),
 ('running-shoes',   'pair of running trainers sneakers'),
 # Places and context
 ('living-room',     'modern living room interior sofa'),
 ('living-room',     'small apartment interior room'),
 ('bedroom',         'simple bedroom interior bed'),
 ('window-light',    'sunlight through window indoor morning'),
 ('stairs-home',     'staircase steps indoor home'),
 ('park-run',        'person jogging outdoor park path'),
 ('walking',         'person walking outdoors path'),
 # Habit, recovery, food
 ('sleep',           'person sleeping in bed'),
 ('sleep',           'bed pillow bedroom sleep'),
 ('notebook',        'notebook and pen on desk planner'),
 ('calendar',        'calendar planner schedule desk'),
 ('clock',           'alarm clock morning time'),
 ('protein-food',    'healthy meal plate vegetables'),
 ('protein-food',    'eggs protein food breakfast'),
 ('breakfast',       'healthy breakfast bowl oats fruit'),
 ('towel',           'folded towel bathroom textile'),
 ('coffee',          'cup of coffee morning table'),
]

# Openverse matches on titles, so a search for an everyday word drags in museum
# objects and manuscripts. Anything whose title trips these is skipped.
JUNK = ('clipart', 'vector', 'illustration', 'manuscript', 'romance of', 'painting',
        'moccasin', 'museum', 'temple', 'cathedral', 'church', 'nebula', 'lobster',
        'starfish', 'coromandel', 'cabinet', 'antique', 'sculpture', 'statue',
        'engraving', 'lithograph', 'drawing', 'poster', 'map of', 'coat of arms',
        'nude', 'logo', 'icon', 'diagram', 'chart')


def thumb_url(url, width=THUMB_W):
    """Rewrite a Commons original into its thumbnail, so we pull ~300 KB rather
    than a 7 MB original. Non-Commons URLs are returned unchanged."""
    m = re.match(r'(https://upload\.wikimedia\.org/wikipedia/commons)/([0-9a-f])/([0-9a-f]{2})/(.+)$', url)
    if not m or '/thumb/' in url:
        return url
    base, d1, d2, name = m.groups()
    if not name.lower().endswith(('.jpg', '.jpeg', '.png')):
        return url
    return '%s/thumb/%s/%s/%s/%dpx-%s' % (base, d1, d2, name, width, name)


def fetch(url, tries=4):
    """Download with backoff. 429 means we are going too fast, so wait longer."""
    for i in range(tries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=90).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(4 * (i + 1))
                continue
            return None
        except Exception:
            return None
    return None


def search(term, n=20, page=1):
    u = ('https://api.openverse.org/v1/images/?q=%s'
         '&license_type=commercial,modification&size=large&mature=false'
         '&page_size=%d&page=%d'
         % (urllib.parse.quote(term), n, page))
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=45))
    except Exception as e:
        print('  search failed: %s' % str(e)[:60])
        return []
    return r.get('results', [])


def main():
    os.makedirs(OUT, exist_ok=True)
    pool, seen_title, seen_url = [], set(), set()
    for key, term in QUERIES:
        hits = search(term, 20, 1) + search(term, 20, 2)
        kept = 0
        for h in hits:
            title = (h.get('title') or '').lower()
            if any(j in title for j in JUNK):
                continue
            if title in seen_title or h.get('url') in seen_url:
                continue
            w, hh = h.get('width') or 0, h.get('height') or 0
            if w < MIN_W or hh < MIN_H:
                continue
            url = h.get('url')
            if not url:
                continue
            name = '%s-%s.jpg' % (key, hashlib.md5(url.encode()).hexdigest()[:8])
            path = os.path.join(OUT, name)
            if not os.path.exists(path):
                data = fetch(thumb_url(url))
                time.sleep(PAUSE)
                if not data or len(data) < 25000:
                    continue
                open(path, 'wb').write(data)
            seen_title.add(title)
            seen_url.add(h.get('url'))
            pool.append({
                'key': key, 'query': term, 'file': name,
                'title': h.get('title'), 'creator': h.get('creator'),
                'creator_url': h.get('creator_url'),
                'license': h.get('license'), 'license_version': h.get('license_version'),
                'license_url': h.get('license_url'),
                'source': h.get('source'), 'landing': h.get('foreign_landing_url'),
                'width': w, 'height': hh,
            })
            kept += 1
            if kept >= 3:
                break
        print('%-16s %d kept' % (key, kept))
    json.dump(pool, open(POOL, 'w'), indent=1)
    print('\npool: %d images -> %s' % (len(pool), POOL))


if __name__ == '__main__':
    main()
