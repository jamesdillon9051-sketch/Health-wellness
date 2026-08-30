# -*- coding: utf-8 -*-
"""Point the whole site at your real domain.

The build ships with the placeholder https://healthwellness.com in 1,279 places
— canonical tags, Open Graph and Twitter URLs, JSON-LD @id fields, sitemap.xml
and robots.txt. Getting one wrong costs you duplicate-content problems and
broken share previews, so this rewrites all of them together.

Usage:
    python3 tools/set_domain.py https://yourdomain.com          # apply
    python3 tools/set_domain.py https://yourdomain.com --dry    # preview only

Run it again any time you move domains — it rewrites whatever is currently
there, not just the original placeholder.
"""
import glob, io, os, re, sys

STATE = 'tools/.domain'
DEFAULT = 'https://healthwellness.com'


def targets():
    return (sorted(glob.glob('*.html') + glob.glob('posts/*.html')
                   + glob.glob('categories/*.html'))
            + ['sitemap.xml', 'robots.txt', 'README.md', 'tools/render.py'])


def current():
    if os.path.exists(STATE):
        return io.open(STATE, encoding='utf-8').read().strip()
    return DEFAULT


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    if len(args) != 1:
        print(__doc__)
        return 1

    new = args[0].rstrip('/')
    if not re.match(r'^https?://[a-z0-9.-]+\.[a-z]{2,}$', new, re.I):
        print('Not a valid site root: %r\nExpected something like https://example.com' % new)
        return 1
    if not new.startswith('https://'):
        print('Warning: %s is not HTTPS. Search engines and browsers will '
              'penalise that; continuing anyway.' % new)

    old = current()
    if old == new:
        print('Already set to %s — nothing to do.' % new)
        return 0

    total = files = 0
    for f in targets():
        if not os.path.exists(f):
            continue
        src = io.open(f, encoding='utf-8').read()
        n = src.count(old)
        if not n:
            continue
        total += n
        files += 1
        if not dry:
            io.open(f, 'w', encoding='utf-8').write(src.replace(old, new))

    if dry:
        print('Would rewrite %d occurrences of %s across %d files.' % (total, old, files))
    else:
        io.open(STATE, 'w', encoding='utf-8').write(new + '\n')
        print('Rewrote %d occurrences across %d files.' % (total, files))
        print('%s  ->  %s' % (old, new))
        print('\nNow re-run:  python3 tools/audit.py && python3 tools/linkcheck.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
