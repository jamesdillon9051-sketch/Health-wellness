# -*- coding: utf-8 -*-
"""Render SVG files to JPEG through headless Chromium.

Chromium is used rather than an image library because it gives real stroke
joins, curves and text layout — the line art has to look drawn, not plotted.
"""
import os, sys
from playwright.sync_api import sync_playwright

FONTS = '/mnt/skills/examples/canvas-design/canvas-fonts'
FACES = [('Bricolage Grotesque', 'BricolageGrotesque-Bold.ttf', 700),
         ('Bricolage Grotesque', 'BricolageGrotesque-Regular.ttf', 400),
         ('IBM Plex Mono', 'IBMPlexMono-Bold.ttf', 700),
         ('IBM Plex Mono', 'IBMPlexMono-Regular.ttf', 400)]


def _face_css():
    out = []
    for fam, fn, wt in FACES:
        p = os.path.join(FONTS, fn)
        if os.path.exists(p):
            out.append("@font-face{font-family:'%s';src:url('file://%s');font-weight:%d;}"
                       % (fam, p, wt))
    return ''.join(out)


def render(jobs, quality=86):
    """jobs: list of (svg_string, out_path, width, height)."""
    css = _face_css()
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
        pg = b.new_page()
        for svg, out, w, h in jobs:
            pg.set_viewport_size({'width': w, 'height': h})
            pg.set_content('<style>%shtml,body{margin:0;padding:0;background:#E9EDF1}'
                           'svg{display:block}</style>%s' % (css, svg),
                           wait_until='load')
            pg.wait_for_timeout(60)
            d = os.path.dirname(out)
            if d:
                os.makedirs(d, exist_ok=True)
            pg.screenshot(path=out, type='jpeg', quality=quality,
                          clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        b.close()
