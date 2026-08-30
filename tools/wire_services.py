# -*- coding: utf-8 -*-
"""Wire config.js / forms.js / ads.js into every page, and upgrade the forms.

Idempotent: safe to re-run. Touches only the hand-copied blocks, so the pages
stay plain editable HTML with no build step.

Run:  python3 tools/wire_services.py
"""
import glob, io, os, re

HONEYPOT = ('<input type="text" name="_gotcha" tabindex="-1" autocomplete="off" '
            'aria-hidden="true" class="visually-hidden">')
STATUS = '<p class="form-status" role="status" aria-live="polite" hidden></p>'

files = sorted(set(glob.glob('*.html') + glob.glob('posts/*.html')
                   + glob.glob('categories/*.html')))
changed = 0

for f in files:
    depth = '../' if os.path.dirname(f) else ''
    src = orig = io.open(f, encoding='utf-8').read()

    # --- 1. scripts: config before main, forms + ads after -----------------
    main_tag = '<script src="%sassets/js/main.js" defer></script>' % depth
    if main_tag in src and 'assets/js/config.js' not in src:
        src = src.replace(main_tag,
            '<script src="%sassets/js/config.js"></script>\n' % depth +
            main_tag +
            '\n<script src="%sassets/js/forms.js" defer></script>' % depth +
            '\n<script src="%sassets/js/ads.js" defer></script>' % depth)

    # --- 2. signup forms: placeholder -> real, wired form ------------------
    src = src.replace('<form class="signup__form" data-placeholder action="#" method="post">',
                      '<form class="signup__form" data-form="signup" action="#" method="post">')

    # --- 3. contact form gets the same treatment --------------------------
    src = re.sub(r'<form action="https://formspree\.io/f/YOUR_FORM_ID" method="POST"',
                 '<form data-form="contact" action="https://formspree.io/f/YOUR_FORM_ID" method="POST"',
                 src)

    # --- 4. honeypot + status region inside every wired form --------------
    def fill(m):
        body = m.group(0)
        if 'name="_gotcha"' in body:
            return body
        indent = re.search(r'\n(\s*)<button', body)
        pad = indent.group(1) if indent else '        '
        return body.replace('</form>',
                            '%s%s\n%s%s\n%s</form>' % (pad, HONEYPOT, pad, STATUS,
                                                       pad[:-2] if len(pad) > 2 else pad))
    src = re.sub(r'<form[^>]*data-form="[^"]*"[^>]*>.*?</form>', fill, src, flags=re.S)

    if src != orig:
        io.open(f, 'w', encoding='utf-8').write(src)
        changed += 1

print('%d of %d files updated' % (changed, len(files)))
