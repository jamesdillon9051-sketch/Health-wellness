# -*- coding: utf-8 -*-
"""Verify every internal link resolves to a file that exists, and that every
in-page anchor target exists. Run before deploying."""
import sys, os, re, io, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

HREF = re.compile(r'href="([^"#][^"]*)"')
ANCH = re.compile(r'href="#([^"]+)"')
IDRX = re.compile(r'\bid="([^"]+)"')

bad, checked, anchors_bad = [], 0, []
files = sorted(glob.glob('*.html') + glob.glob('posts/*.html') + glob.glob('categories/*.html'))

for f in files:
    d = os.path.dirname(f)
    s = io.open(f, encoding='utf-8').read()
    ids = set(IDRX.findall(s))

    for a in set(ANCH.findall(s)):
        if a not in ids:
            anchors_bad.append('%s -> #%s' % (f, a))

    for h in set(HREF.findall(s)):
        if h.startswith(('http', 'mailto:', 'tel:', 'data:', '//')):
            continue
        checked += 1
        target = os.path.normpath(os.path.join(d, h.split('#')[0]))
        if not os.path.exists(target):
            bad.append('%s -> %s (missing %s)' % (f, h, target))

print('Files scanned      : %d' % len(files))
print('Internal links     : %d' % checked)
print('Broken links       : %d' % len(bad))
for b in bad[:40]:
    print('   ' + b)
print('Broken anchors     : %d' % len(anchors_bad))
for b in anchors_bad[:40]:
    print('   ' + b)
sys.exit(1 if (bad or anchors_bad) else 0)
