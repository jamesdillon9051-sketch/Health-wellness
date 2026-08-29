# -*- coding: utf-8 -*-
"""
Health Wellness — page renderer.

The published site is plain static HTML with no build step. This module exists
only so the ~115 hand-copied header/footer/head blocks stay byte-identical
across every file; the HTML it writes is the source of truth afterwards and is
safe to edit by hand.

The post registry is parsed from content-map.md so the map and the site cannot
drift apart.
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE   = 'Health Wellness'
DOMAIN = 'https://healthwellness.com'
AUTHOR = 'Sam Reyes'
AUTHOR_BIO = (
    'I am not a doctor, a physiotherapist or a certified strength coach, and I '
    'will not pretend otherwise. I am someone who spent six years failing to keep '
    'a gym habit alive around a full-time job, then rebuilt the whole thing on '
    'about six square feet of floor between a sofa and a radiator. Everything on '
    'this site is what I have tested on myself and cross-checked against the '
    'actual research, cited so you can read it yourself. Where the evidence is '
    'thin or contested, I say so rather than picking whichever study sounds best.'
)

FONTS = ('https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800'
         '&family=IBM+Plex+Sans:wght@400;600&display=swap')

DISCLAIMER = (
    '<strong>Medical disclaimer:</strong> The content on ' + SITE + ' is for general informational\n'
    '      and educational purposes only. It is not medical advice and is not a substitute for\n'
    '      professional diagnosis, treatment or care from a qualified healthcare provider. Always speak\n'
    '      to your doctor or a licensed clinician before starting a new exercise programme, particularly\n'
    '      if you are pregnant, recovering from injury or illness, or managing an existing health\n'
    '      condition. Never disregard professional medical advice or delay seeking it because of\n'
    '      something you have read here.'
)

# ---------------------------------------------------------------- pillars
PILLARS = [
    dict(key='bodyweight-strength', nav='Bodyweight',
         name='Bodyweight Strength',
         tagline='Push-ups to pistol squats. How to actually get stronger without touching a barbell.',
         blurb='Getting genuinely stronger with nothing but your own bodyweight, a floor and a doorframe.'),
    dict(key='quick-workouts', nav='Quick Workouts',
         name='Quick Workouts &amp; Plans',
         tagline='Ready-made sessions and week-by-week plans built for 15–30 minute windows.',
         blurb='Sessions and plans designed around the time you actually have, not the time a programme assumes.'),
    dict(key='small-space-training', nav='Small Space',
         name='Small-Space Training',
         tagline='Thin walls, low ceilings, a toddler underfoot. Training around the room you actually have.',
         blurb='Training in flats, bedrooms, offices and hotel rooms — quietly, and in very little floor space.'),
    dict(key='minimal-gear', nav='Gear',
         name='Minimal Gear',
         tagline="What's worth buying, what's a waste, and what you already own that does the job.",
         blurb='Honest equipment guides for people who want the smallest possible pile of kit.'),
    dict(key='habits-recovery', nav='Habits',
         name='Habits &amp; Recovery',
         tagline='The part nobody writes about: sleep, soreness, protein, and not quitting in week six.',
         blurb='Sleep, soreness, food and the behaviour side — the reasons home training actually fails.'),
]
PILLAR_BY_KEY = dict((p['key'], p) for p in PILLARS)


def load_posts():
    """Parse content-map.md into an ordered post registry."""
    txt = io.open(os.path.join(ROOT, 'content-map.md'), encoding='utf-8').read()
    posts, pillar = [], None
    for line in txt.splitlines():
        # Bind to the category path rather than the display heading — the
        # heading wording drifts, the filename does not.
        m = re.match(r'^`/categories/([a-z-]+)\.html`', line)
        if m:
            pillar = m.group(1)
            assert pillar in PILLAR_BY_KEY, 'unknown pillar: ' + pillar
            continue
        m = re.match(r'^\|\s*(\d+)\s*\|\s*(HUB|·)\s*(✅)?\s*\|\s*(.+?)\s*\|\s*`(.+?)`\s*\|\s*(.+?)\s*\|$', line)
        if m:
            posts.append(dict(
                n=int(m.group(1)),
                kind='hub' if m.group(2) == 'HUB' else 'cluster',
                title=m.group(4).strip(),
                slug=m.group(5).strip(),
                keyword=m.group(6).strip(),
                pillar=pillar,
            ))
    return posts


POSTS = load_posts()
POST_BY_SLUG = dict((p['slug'], p) for p in POSTS)


def in_pillar(key):
    return [p for p in POSTS if p['pillar'] == key]


def hubs(key):
    return [p for p in in_pillar(key) if p['kind'] == 'hub']


# ---------------------------------------------------------------- chrome
def _pre(depth):
    return '../' if depth else ''


def head(depth, title_tag, description, url_path, og_image=None,
         og_type='website', extra_meta='', jsonld=(), published=None, updated=None):
    p = _pre(depth)
    img = og_image or (DOMAIN + '/assets/images/site/og-default.jpg')
    art = ''
    if og_type == 'article':
        art = ('<meta property="article:published_time" content="%s">\n'
               '<meta property="article:modified_time" content="%s">\n' % (published, updated))
    ld = '\n'.join('<script type="application/ld+json">\n%s\n</script>' % b for b in jsonld)
    return u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{domain}/{path}">
<meta name="theme-color" content="#0C1A24">
<meta name="author" content="{author}">

<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{domain}/{path}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_GB">
{art}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
{extra}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/style.css">
<script src="{p}assets/js/main.js" defer></script>

{ld}
</head>
<body>
""".format(title=title_tag, desc=description, domain=DOMAIN, path=url_path,
           author=AUTHOR, ogtype=og_type, site=SITE, img=img, art=art,
           extra=extra_meta, fonts=FONTS, p=p, ld=ld)


def header(depth, active=None):
    """The shared header. Byte-identical everywhere except link depth."""
    p = _pre(depth)
    items = []
    mobile = []
    for pl in PILLARS:
        cur = ' aria-current="page"' if active == pl['key'] else ''
        items.append('        <li><a class="nav__link" href="%scategories/%s.html"%s>%s</a></li>'
                     % (p, pl['key'], cur, pl['nav']))
        mobile.append('      <li><a class="mobile-nav__link" href="%scategories/%s.html">%s</a></li>'
                      % (p, pl['key'], pl['name']))
    cur_about = ' aria-current="page"' if active == 'about' else ''
    items.append('        <li><a class="nav__link" href="%sabout.html"%s>About</a></li>' % (p, cur_about))
    mobile.append('      <li><a class="mobile-nav__link" href="%sabout.html">About</a></li>' % p)
    mobile.append('      <li><a class="mobile-nav__link" href="%scontact.html">Contact</a></li>' % p)

    return u"""
<a class="skip-link" href="#main">Skip to content</a>

<!-- ===== SHARED HEADER — keep identical across all pages ===== -->
<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand" href="{p}index.html">
      <span class="brand__mark" aria-hidden="true"></span>
      <span class="brand__name">{site}</span>
    </a>

    <nav class="nav" aria-label="Primary">
      <ul class="nav__list">
{items}
      </ul>
    </nav>

    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>

  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile" hidden>
    <ul class="mobile-nav__list">
{mobile}
    </ul>
  </nav>
</header>
<!-- ===== /SHARED HEADER ===== -->
""".format(p=p, site=SITE, items='\n'.join(items), mobile='\n'.join(mobile))


def footer(depth):
    """The shared footer. Byte-identical everywhere except link depth."""
    p = _pre(depth)
    topics = '\n'.join(
        '          <li><a href="%scategories/%s.html">%s</a></li>' % (p, pl['key'], pl['name'])
        for pl in PILLARS)
    return u"""
<!-- ===== SHARED FOOTER — keep identical across all pages ===== -->
<footer class="site-footer">
  <div class="wrap">

    <div class="ad-slot ad-slot--footer" data-ad-slot="footer-leaderboard"></div>

    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{p}index.html">
          <span class="brand__mark" aria-hidden="true"></span>
          <span class="brand__name">{site}</span>
        </a>
        <p>Home strength training for people with no gym, no commute time and no patience for fitness industry nonsense. Written by one person, tested in one small flat.</p>
      </div>

      <div class="footer-col">
        <h3>Topics</h3>
        <ul>
{topics}
        </ul>
      </div>

      <div class="footer-col">
        <h3>Site</h3>
        <ul>
          <li><a href="{p}about.html">About</a></li>
          <li><a href="{p}contact.html">Contact</a></li>
          <li><a href="{p}privacy-policy.html">Privacy Policy</a></li>
          <li><a href="{p}medical-disclaimer.html">Medical Disclaimer</a></li>
        </ul>
      </div>
    </div>

    <p class="footer-disclaimer">
      {disc}
      <a href="{p}medical-disclaimer.html">Read the full disclaimer</a>.
    </p>

    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> {site}. All rights reserved.</span>
      <span>Built as a static site. No trackers beyond basic analytics.</span>
    </div>
  </div>
</footer>
<!-- ===== /SHARED FOOTER ===== -->

<button class="to-top" type="button" aria-label="Back to top">&uarr;</button>

</body>
</html>
""".format(p=p, site=SITE, topics=topics, disc=DISCLAIMER)


def signup(form_id, heading='Get one workout a week',
           blurb='A session you can do in your living room, plus one thing worth reading. Nothing else.',
           inline=True):
    cls = 'signup signup--inline' if inline else 'signup'
    return u"""
  <section class="{cls}">
    <div class="signup__inner">
      <h2>{h}</h2>
      <p>{b}</p>
      <form class="signup__form" data-placeholder action="#" method="post">
        <label class="visually-hidden" for="{fid}">Email address</label>
        <input type="email" id="{fid}" name="email" placeholder="you@example.com" required autocomplete="email">
        <button class="btn btn--accent" type="submit">Send it</button>
      </form>
      <p class="signup__note">No spam. Unsubscribe in one click.</p>
    </div>
  </section>
""".format(cls=cls, h=heading, b=blurb, fid=form_id)


def write(relpath, html):
    full = os.path.join(ROOT, relpath)
    d = os.path.dirname(full)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(full, 'w', encoding='utf-8').write(html)
    return relpath
