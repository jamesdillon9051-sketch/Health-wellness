# -*- coding: utf-8 -*-
"""Rebuild the homepage front as a magazine mosaic.

Replaces the single full-width hero with the layout a news front page uses: one
lead story plus a 2x2 of seconds, every cell an image tile with a category
badge and an overlaid headline, then a four-across strip below.

More entry points above the fold, and colour doing the sorting. Idempotent.

Run:  python3 tools/homepage_mosaic.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import excerpts

LEAD = '4-week-home-workout-plan'
SECONDS = ['15-minute-full-body-workout', 'quiet-home-workouts',
           'minimalist-home-gym-guide', 'stick-to-home-workout-habit']
STRIP = ['no-jump-cardio', 'push-up-progressions-for-beginners',
         'one-dumbbell-workout', 'workout-at-home-with-kids']

LABEL = {'bodyweight-strength': 'Bodyweight', 'quick-workouts': 'Quick workouts',
         'small-space-training': 'Small space', 'minimal-gear': 'Gear',
         'habits-recovery': 'Habits'}


def excerpt(slug):
    fn = getattr(excerpts, 'EXCERPTS', None)
    if isinstance(fn, dict):
        return fn.get(slug, '')
    return ''


def tile(slug, lead=False, indent='      '):
    m = R.POST_BY_SLUG[slug]
    p = m['pillar']
    parts = [
      '%s<a class="tile" href="posts/%s.html" data-pillar="%s">' % (indent, slug, p),
      '%s  <img src="assets/images/%s/%s-cover.jpg" alt="" width="1200" height="900" loading="lazy">'
        % (indent, slug, slug),
      '%s  <span class="tile__body">' % indent,
      '%s    <span class="tile__badge">%s</span>' % (indent, LABEL[p]),
      '%s    <span class="tile__title">%s</span>' % (indent, m['title']),
    ]
    if lead:
        ex = excerpt(slug)
        if ex:
            parts.append('%s    <span class="tile__standfirst">%s</span>' % (indent, ex))
    parts += ['%s    <span class="tile__meta">Sam Reyes</span>' % indent,
              '%s  </span>' % indent,
              '%s</a>' % indent]
    return '\n'.join(parts)


def main():
    src = io.open('index.html', encoding='utf-8').read()
    if 'class="mosaic"' in src:
        print('mosaic already present — nothing to do')
        return

    mosaic = '\n'.join([
      '  <!-- FRONT PAGE MOSAIC -->',
      '  <section class="section section--flush-top wrap">',
      '    <div class="mosaic">',
      tile(LEAD, lead=True),
      '\n'.join(tile(s) for s in SECONDS),
      '    </div>',
      '',
      '    <div class="section-tab">',
      '      <h2>More this week</h2>',
      '      <span class="meta">Four to start with</span>',
      '    </div>',
      '    <div class="strip">',
      '\n'.join(tile(s) for s in STRIP),
      '    </div>',
      '  </section>',
    ])

    # swap the hero band for the mosaic
    start = src.index('  <!-- HERO -->')
    end = src.index('  <!-- AD SLOT: header leaderboard')
    src = src[:start] + mosaic + '\n\n' + src[end:]
    io.open('index.html', 'w', encoding='utf-8').write(src)
    print('homepage front replaced with the mosaic')


if __name__ == '__main__':
    main()
