# -*- coding: utf-8 -*-
"""Create credits.html, reusing the shared chrome from an existing static page.

Attribution for CC-BY images is a licence condition. The page is generated from
photo-pool.json so it cannot drift from what is actually on the site.

Run:  python3 tools/build_credits_page.py
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_credits as MC

SRC = 'privacy-policy.html'
DST = 'credits.html'

TITLE = 'Image credits'
DESC = ('Every photograph on this site, who took it, and the licence it is used '
        'under. Generated from the image manifest, not maintained by hand.')


def main():
    base = io.open(SRC, encoding='utf-8').read()

    rows = MC.rows()
    needs = [r for r in rows if r[3].startswith('CC BY')]
    table = '\n'.join(
        '        <tr>\n'
        '          <td><a href="%s" rel="nofollow noopener">%s</a></td>\n'
        '          <td>%s</td>\n'
        '          <td><a href="%s" rel="nofollow noopener">%s</a></td>\n'
        '        </tr>' % (
            MC.esc(landing), MC.esc(title),
            ('<a href="%s" rel="nofollow noopener">%s</a>' % (MC.esc(wu), MC.esc(who)))
            if wu else MC.esc(who),
            MC.esc(lu), MC.esc(lic))
        for title, who, wu, lic, lu, landing, source in rows)

    main_html = '''<main id="main">
  <div class="wrap">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="index.html">Home</a></li>
        <li aria-current="page">Image credits</li>
      </ol>
    </nav>

    <header class="page-head">
      <p class="eyebrow">Attribution</p>
      <h1>Image credits</h1>
      <p class="lede">Every photograph used on this site, who took it, and the
        licence it is used under.</p>
    </header>
  </div>

  <div class="wrap prose" style="max-width:60rem">
    <p>The photographs here come from <a href="https://openverse.org/"
      rel="nofollow noopener">Openverse</a>, which indexes openly licensed images
      from Wikimedia Commons, Flickr and others. Every one is licensed for
      commercial use and modification.</p>

    <p><strong>%d of the %d images are CC BY</strong>, which requires
      attribution — that is a condition of the licence, not a courtesy. The
      credits below satisfy it. The rest are CC0 or public domain and need no
      attribution, but are listed anyway.</p>

    <p>This page is generated from the site's image manifest by
      <code>tools/build_credits_page.py</code>, so it cannot fall out of step
      with what is actually published. If you replace an image, re-run it.</p>

    <table>
      <thead>
        <tr><th>Image</th><th>Photographer</th><th>Licence</th></tr>
      </thead>
      <tbody>
%s
      </tbody>
    </table>
  </div>
</main>''' % (len(needs), len(rows), table)

    out = re.sub(r'<main id="main">.*?</main>', lambda _: main_html, base, flags=re.S)
    out = re.sub(r'<title>.*?</title>', '<title>%s — Health Wellness</title>' % TITLE, out, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href="https://healthwellness\.com/)[^"]*(")',
                 lambda m: m.group(1) + 'credits.html' + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                 lambda m: m.group(1) + TITLE + m.group(2), out, count=1)
    io.open(DST, 'w', encoding='utf-8').write(out)
    print('credits.html written: %d images, %d needing attribution' % (len(rows), len(needs)))


if __name__ == '__main__':
    main()
