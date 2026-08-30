# -*- coding: utf-8 -*-
"""Rebuild the homepage front for the calm direction.

Replaces the magazine mosaic with the shape the reference uses: a full-bleed
hero carrying the promise, three cards naming what the site covers, then the
latest guides as a plain three-across grid. Idempotent.

Run:  python3 tools/calm_homepage.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
import excerpts

HERO = '4-week-home-workout-plan'
PROMISES = [
    ('minimal-gear', 'categories/minimal-gear.html', 'No equipment needed',
     'What is worth buying, what is a waste, and what you already own that does the job.'),
    ('quick-workouts', 'categories/quick-workouts.html', 'Fifteen to thirty minutes',
     'Ready-made sessions and week-by-week plans built for the time you actually have.'),
    ('small-space-training', 'categories/small-space-training.html', 'Room for a mat',
     'Thin walls, low ceilings, a toddler underfoot. Training around the home you have.'),
]
LATEST = ['15-minute-full-body-workout', 'quiet-home-workouts', 'minimalist-home-gym-guide',
          'stick-to-home-workout-habit', 'no-jump-cardio', 'perfect-push-up-form']
LABEL = {'bodyweight-strength': 'Bodyweight', 'quick-workouts': 'Quick workouts',
         'small-space-training': 'Small space', 'minimal-gear': 'Gear',
         'habits-recovery': 'Habits'}


def card(slug):
    m = R.POST_BY_SLUG[slug]
    ex = excerpts.EXCERPTS.get(slug, '')
    return '''        <article class="card" data-pillar="%s">
          <a class="card__media" href="posts/%s.html" tabindex="-1" aria-hidden="true">
            <img src="assets/images/%s/%s-cover.jpg" alt="" width="1200" height="900" loading="lazy">
          </a>
          <div class="card__body">
            <p class="eyebrow">%s</p>
            <h3 class="card__title"><a href="posts/%s.html">%s</a></h3>
            <p class="card__excerpt">%s</p>
          </div>
        </article>''' % (m['pillar'], slug, slug, slug, LABEL[m['pillar']], slug,
                         m['title'], ex)


def main():
    src = io.open('index.html', encoding='utf-8').read()
    if 'class="calm-hero"' in src:
        print('calm homepage already in place')
        return

    hero = R.POST_BY_SLUG[HERO]
    promises = '\n'.join('''        <a class="promise" href="%s" data-pillar="%s">
          <span class="promise__mark" aria-hidden="true"></span>
          <span class="promise__title">%s</span>
          <span class="promise__text">%s</span>
        </a>''' % (href, pillar, title, text) for pillar, href, title, text in PROMISES)

    front = '''  <!-- CALM HERO -->
  <section class="calm-hero">
    <img class="calm-hero__bg" src="assets/images/%s/%s-cover.jpg" alt="" width="1200" height="900">
    <div class="wrap calm-hero__inner">
      <p class="eyebrow">No gym &middot; No commute</p>
      <h1>You don't need a gym.<br>You need twenty minutes<br>and a bit of floor.</h1>
      <p class="calm-hero__lede">Honest, tested home training for people with a full-time
        job, a small flat, and no interest in a monthly direct debit they will use twice.</p>
      <a class="btn btn--accent" href="posts/%s.html">Start the 4-week plan</a>
    </div>
  </section>

  <!-- WHAT THIS COVERS -->
  <section class="section wrap">
    <div class="promises">
%s
    </div>
  </section>

  <!-- LATEST -->
  <section class="section wrap">
    <div class="section-tab">
      <h2>Latest guides</h2>
      <span class="meta"><a href="categories/quick-workouts.html">Browse all 100 &rarr;</a></span>
    </div>
    <div class="grid grid--3">
%s
    </div>
  </section>
''' % (HERO, HERO, HERO, promises, '\n'.join(card(s) for s in LATEST))

    start = src.index('  <!-- FRONT PAGE MOSAIC -->')
    end = src.index('  <!-- AD SLOT: header leaderboard')
    src = src[:start] + front + '\n' + src[end:]
    io.open('index.html', 'w', encoding='utf-8').write(src)
    print('homepage rebuilt: hero, three promises, six latest guides')


if __name__ == '__main__':
    main()
