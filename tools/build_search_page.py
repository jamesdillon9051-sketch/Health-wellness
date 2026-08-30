# -*- coding: utf-8 -*-
"""Create search.html, reusing the shared chrome from an existing static page.

Search on a static site needs JavaScript, so this page is built to be useful
without it: every one of the 100 guides is listed, grouped by section, as plain
links. With JavaScript the same page becomes a live filter, and the browse list
hides once you start typing.

Run:  python3 tools/build_search_page.py
"""
import io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R

SRC, DST = 'privacy-policy.html', 'search.html'
LABEL = {'bodyweight-strength': 'Bodyweight Strength',
         'quick-workouts': 'Quick Workouts & Plans',
         'small-space-training': 'Small-Space Training',
         'minimal-gear': 'Minimal Gear',
         'habits-recovery': 'Habits & Recovery'}
ORDER = ['bodyweight-strength', 'quick-workouts', 'small-space-training',
         'minimal-gear', 'habits-recovery']


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    base = io.open(SRC, encoding='utf-8').read()

    groups = []
    for pillar in ORDER:
        posts = [p for p in R.POSTS if p['pillar'] == pillar]
        items = '\n'.join(
            '          <li><a href="posts/%s.html">%s</a></li>' % (p['slug'], esc(p['title']))
            for p in posts)
        groups.append(
            '      <section class="section" data-pillar="%s">\n'
            '        <div class="section-tab"><h2>%s</h2>'
            '<span class="meta">%d guides</span></div>\n'
            '        <ul class="post-index">\n%s\n        </ul>\n'
            '      </section>' % (pillar, esc(LABEL[pillar]), len(posts), items))

    main_html = '''<main id="main">
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="index.html">Home</a></li>
        <li aria-current="page">Search</li>
      </ol>
    </nav>

    <header class="page-head">
      <p class="eyebrow">100 guides</p>
      <h1>Search</h1>
      <p class="lede">Every guide on the site. Type to filter, or browse by
        section below.</p>
    </header>

    <div class="search-page" data-search-page hidden>
      <form class="search__form" role="search">
        <label class="visually-hidden" for="q">Search guides</label>
        <input id="q" type="search" autocomplete="off" placeholder="Search 100 guides…">
      </form>
      <div class="search__results" aria-live="polite"></div>
    </div>

    <div data-search-browse>
%s
    </div>
  </div>
</main>''' % ('\n\n'.join(groups))

    out = re.sub(r'<main id="main">.*?</main>', lambda _: main_html, base, flags=re.S)
    out = re.sub(r'<title>.*?</title>', '<title>Search — Health Wellness</title>', out, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + 'Search all 100 home-workout guides, or browse '
                 'them by section.' + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href="https://healthwellness\.com/)[^"]*(")',
                 lambda m: m.group(1) + 'search.html' + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                 lambda m: m.group(1) + 'Search' + m.group(2), out, count=1)
    io.open(DST, 'w', encoding='utf-8').write(out)
    print('search.html written: %d guides listed for the no-JS case' % len(R.POSTS))


if __name__ == '__main__':
    main()
