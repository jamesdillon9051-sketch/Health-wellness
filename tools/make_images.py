# -*- coding: utf-8 -*-
"""Draw every image the site uses, from scratch.

All artwork is generated line art — no stock photography, no third-party assets,
so nothing here carries a licence, an attribution requirement or a takedown risk.

Each hero pairs a posed figure (or a diagram) with the post's own first three
section headings, so the image is a visual contents page for that specific post
rather than decoration. Headings are read out of the built HTML, never invented.

Run:  python3 tools/make_images.py
"""
import glob, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import figures as F
import compose as C
import rasterize

PILLAR_LABEL = {
    'bodyweight-strength': 'Bodyweight strength',
    'quick-workouts':      'Quick workouts',
    'small-space-training':'Small-space training',
    'minimal-gear':        'Minimal gear',
    'habits-recovery':     'Habits & recovery',
}

# Slug keyword -> (layout, poses, panel labels). First match wins, so the
# specific patterns are listed before the general ones.
RULES = [
 (r'kettlebell|swing',                   ('two', 'hinge', 'squat-bot', 'hinge', 'squat')),
 (r'dumbbell',                           ('two', 'squat-bot', 'row', 'squat', 'row')),
 (r'weighted-vest',                      ('two', 'pushup-top', 'squat-bot', 'loaded push', 'loaded squat')),
 (r'workout-bench|bench',                ('two', 'dip', 'pushup-top', 'dip', 'press')),
 (r'yoga-mat|exercise-mat|mat\b',        ('two', 'plank', 'bridge', 'plank', 'bridge')),
 (r'slider',                             ('two', 'mtn-climber', 'plank', 'slide', 'brace')),
 (r'loop-band|tube-band|resistance-band|bands', ('two', 'row', 'squat-bot', 'pull', 'press')),
 (r'sandbag|rucksack|diy-home-gym',      ('two', 'hinge', 'lunge', 'carry', 'lunge')),
 (r'home-gym-under-100|cheap-home-gym|minimalist-home-gym|home-gym-corner|storing',
                                         ('two', 'squat-top', 'row', 'stand', 'pull')),
 (r'\bapps?\b|tracking|progress|results', ('two', 'stand', 'squat-top', 'week 1', 'week 8')),
 (r'lunch-break|short-workouts|5-minute|15-minute|10-minute|20-minute|30-minute',
                                         ('two', 'jack', 'pushup-top', 'raise HR', 'strength')),
 (r'studio-flat|small-apartment|how-much-space', ('two', 'plank', 'squat-top', 'floor', 'standing')),
 (r'build-muscle|strength-training-at-home|full-body', ('two', 'pushup-top', 'row', 'push', 'pull')),
 (r'push-up|pushup|perfect-push',        ('two', 'pushup-top', 'pushup-bot', 'start', 'bottom')),
 (r'chest',                              ('two', 'pushup-top', 'pushup-bot', 'start', 'bottom')),
 (r'squat-form|bodyweight-squat',        ('two', 'squat-top', 'squat-bot', 'stand', 'depth')),
 (r'pistol',                             ('two', 'squat-top', 'pistol', 'two legs', 'one leg')),
 (r'bulgarian|lunge',                    ('one', 'lunge', 'split stance')),
 (r'pull-up|pullup|first-pull',          ('two', 'hang', 'pullup', 'hang', 'chin over')),
 (r'doorway|rings|suspension',           ('two', 'hang', 'pullup', 'hang', 'pull')),
 (r'\brow\b|rows|back-exercises',        ('one', 'row', 'inverted row')),
 (r'dip',                                ('one', 'dip', 'parallel bars')),
 (r'plank|core|ab-wheel|silent-ab|situp|sit-up', ('two', 'plank', 'side-plank', 'front', 'side')),
 (r'glute|bridge|hip',                   ('two', 'bridge', 'hinge', 'bridge', 'hinge')),
 (r'leg-workout|legs|calf',              ('two', 'squat-bot', 'calf-raise', 'squat', 'calf raise')),
 (r'handstand',                          ('two', 'plank', 'handstand', 'build-up', 'inverted')),
 (r'shoulder|arm-workout|arms',          ('two', 'pushup-top', 'dip', 'press', 'dip')),
 (r'hiit|cardio|jump-rope|jumping|no-jump', ('two', 'jack', 'high-knee', 'jack', 'high knee')),
 (r'stair|step',                         ('one', 'high-knee', 'stair climb')),
 (r'mobility|stretch|cool-down|warm-up', ('two', 'hinge', 'bird-dog', 'hinge', 'bird dog')),
 (r'foam-rolling|doms|soreness|recovery|sleep|rest|deload', ('two', 'bridge', 'dead-bug', 'release', 'control')),
 (r'desk|office|posture|sit',            ('two', 'sit-tall', 'hinge', 'seated', 'stand up')),
 (r'quiet|noise|apartment|neighbour|carpet|floor|bedroom|low-ceiling', ('two', 'squat-bot', 'plank', 'low impact', 'floor work')),
 (r'kids|parent|family',                 ('two', 'plank', 'mtn-climber', 'hold', 'move')),
 (r'circuit|emom|finisher|interval',     ('two', 'jack', 'mtn-climber', 'work', 'work')),
 (r'wall',                               ('one', 'wall-sit', 'wall sit')),
 (r'band|dumbbell|kettlebell|vest|bench|mat|slider|equipment|gear|gym|storage|buy|cheap|under-100|app',
                                         ('two', 'squat-top', 'hinge', 'load it', 'move it')),
 (r'travel|hotel|balcony|outdoor',       ('two', 'pushup-top', 'lunge', 'press', 'lunge')),
 (r'protein|nutrition|meal|eat|weight-loss', ('two', 'stand', 'squat-bot', 'fuel', 'train')),
 (r'schedule|split|4-week|weekly|how-many-days|routine|plan\b|structure|frequency',
                                         ('week',)),
 (r'habit|motivation|consistency|stick|restart|drop-off|six-week|morning-vs|evening|shift-work|tired',
                                         ('week',)),
 (r'how-long|space|long',                ('two', 'stand', 'squat-top', 'week 1', 'week 8')),
]

FALLBACK = {
 'bodyweight-strength': ('two', 'pushup-top', 'squat-bot', 'push', 'squat'),
 'quick-workouts':      ('two', 'jack', 'squat-bot', 'fast', 'strong'),
 'small-space-training':('two', 'plank', 'squat-bot', 'floor', 'standing'),
 'minimal-gear':        ('two', 'squat-top', 'hinge', 'load it', 'move it'),
 'habits-recovery':     ('two', 'stand', 'bridge', 'show up', 'recover'),
}

H2 = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
TAG = re.compile(r'<[^>]+>')
BRIEF = re.compile(
    r'<!--\s*IMAGE BRIEF:\s*(?P<file>[\w\-.]+)\s*\((?P<dims>[^)]+)\)'
    r'(?P<body>.*?)-->\s*<img\s+src="(?P<src>[^"]+)"', re.S)


import html as _html


def plain(frag):
    """Tags out, entities decoded. The SVG writer re-escapes, so decoding here
    stops '&amp;' surviving into the artwork as '&amp;amp;'."""
    return re.sub(r'\s+', ' ', _html.unescape(TAG.sub('', frag))).strip()


def headings(html, n=3):
    out = []
    for h in H2.findall(html):
        t = plain(h)
        if not t or t.lower().startswith(("what's in this guide", 'sources', 'frequently asked')):
            continue
        out.append(t if len(t) <= 40 else t[:38].rstrip(' ,;:') + '…')
        if len(out) == n:
            break
    return out


def plan_for(slug, pillar):
    for pat, spec in RULES:
        if re.search(pat, slug):
            return spec
    return FALLBACK[pillar]


def short_title(t, limit=54):
    t = re.split(r':\s', t)[0]
    return t if len(t) <= limit else t[:limit - 1].rstrip(' ,') + '…'


DESCRIBE = {
 'two':  '%s \u2014 line diagram comparing the %s and %s positions.',
 'one':  '%s \u2014 line diagram of the %s position.',
 'week': '%s \u2014 diagram of a training week, %d of seven days marked as sessions.',
}


def alt_for(spec, title, sessions=3):
    """Alt text describing the diagram that is actually rendered.

    The IMAGE BRIEF comments still describe photography, in case real photos are
    ever commissioned; alt text has to describe what a reader would actually see.
    """
    t = title.rstrip('.')
    if spec[0] == 'week':
        return DESCRIBE['week'] % (t, sessions)
    if spec[0] == 'one':
        return DESCRIBE['one'] % (t, spec[2])
    return DESCRIBE['two'] % (t, spec[3], spec[4])


def set_alt(filename, alt, files):
    """Rewrite the alt attribute on every <img> pointing at `filename`.

    Matches the whole tag by its src, then swaps the alt inside it, so an img
    whose attributes are split across lines is still handled correctly.
    """
    tag = re.compile(r'<img\b[^>]*?src="[^"]*' + re.escape(filename) + r'"[^>]*?>', re.S)
    n = 0
    for f in files:
        h = io.open(f, encoding='utf-8').read()

        def swap(m):
            t = m.group(0)
            if 'alt="' not in t:
                return t
            return re.sub(r'alt="[^"]*"', 'alt="%s"' % alt.replace('"', "'"), t, count=1)

        new = tag.sub(swap, h)
        if new != h:
            io.open(f, 'w', encoding='utf-8').write(new)
            n += 1
    return n


def build():
    jobs, used_fallback = [], []
    for f in sorted(glob.glob('posts/*.html')):
        slug = os.path.basename(f)[:-5]
        html = io.open(f, encoding='utf-8').read()
        meta = R.POST_BY_SLUG.get(slug)
        if not meta:
            continue
        pillar = meta['pillar']
        m = BRIEF.search(html)
        if not m:
            continue
        out = os.path.normpath(os.path.join('posts', m.group('src')))
        w, h = (int(v) for v in m.group('dims').lower().split('x'))
        spec = plan_for(slug, pillar)
        if spec == FALLBACK[pillar]:
            used_fallback.append(slug)
        cues = headings(html)
        lede = re.search(r'<p class="lede">(.*?)</p>', html, re.S)
        cap = plain(lede.group(1)) if lede else ''
        cap = cap if len(cap) <= 92 else cap[:90].rstrip(' ,;') + '…'
        title = short_title(meta['title'])
        eb = PILLAR_LABEL[pillar]
        sessions = 3
        if spec[0] == 'week':
            n = 3
            mm = re.search(r'(\d)-day', slug)
            if mm:
                n = int(mm.group(1))
            elif 'upper-lower' in slug:
                n = 4
            elif 'push-pull-legs' in slug:
                n = 3
            sessions = n
            svg = C.week_grid(title, eb, cap, sessions=n, cues=cues)
        elif spec[0] == 'two':
            svg = C.two_panel(title, eb, cap, spec[1], spec[2], spec[3], spec[4], cues=cues)
        else:
            svg = C.one_panel(title, eb, cap, spec[1], spec[2], cues=cues)
        set_alt(os.path.basename(out), alt_for(spec, meta['title'], sessions),
                [f, 'index.html'])
        jobs.append((svg, out, w, h))
    return jobs, used_fallback


# The three in-content diagrams, whose briefs call for something other than a
# hero. Labels come from the posts' own exercise lists.
def extras():
    return [
     (C.three_panel(
        'Push-Up Form: One Right, Two Wrong', 'Bodyweight strength',
        'The fault is almost always at the hips, not the arms.',
        [('pushup-sag', 'hips sag', False),
         ('pushup-top', 'straight line', True),
         ('pushup-pike', 'hips piked', False)]),
      'assets/images/perfect-push-up-form/perfect-push-up-form-01.jpg', 1200, 800),
     (C.exercise_grid(
        'The Six Movements, In Order', 'Quick workouts',
        'Forty seconds of work, twenty seconds to change position, twice through.',
        [('squat-bot', 'Bodyweight squat'), ('pushup-top', 'Push-up'),
         ('lunge', 'Reverse lunge'), ('bridge', 'Glute bridge'),
         ('plank', 'Plank shoulder tap'), ('dead-bug', 'Dead bug')]),
      'assets/images/15-minute-full-body-workout/15-minute-full-body-workout-01.jpg', 1200, 800),
     (C.week_grid(
        'Where the Session Fits', 'Quick workouts',
        'Three sessions, the rest of the week walking or resting.',
        sessions=3, note='rest days are not wasted days', w=1200, h=800),
      'assets/images/15-minute-full-body-workout/15-minute-full-body-workout-02.jpg', 1200, 800),
    ]


if __name__ == '__main__':
    jobs, fb = build()
    jobs += extras()
    print('rendering %d diagrams (%d heroes + %d in-content)...'
          % (len(jobs), len(jobs) - 3, 3))
    rasterize.render(jobs, quality=86)
    print('done')
