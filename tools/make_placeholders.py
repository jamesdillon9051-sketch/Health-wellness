# -*- coding: utf-8 -*-
"""Generate on-brand placeholder images at the exact paths the HTML references.

These are NOT the final photographs. They are drafting-style placeholders in the
site palette, each stamped with its own filename and its brief, so that:

  * the site renders complete instead of showing 113 broken-image icons,
  * anyone sourcing the real photo can read the brief off the image itself,
  * dropping in the real photo means overwriting the file — no HTML edits.

Paths and sizes are read from the `<img>` tag that follows each IMAGE BRIEF
comment, so this cannot write to a path the pages do not actually request.

Run:  python3 tools/make_placeholders.py
"""
import glob, os, re, io
from PIL import Image, ImageDraw, ImageFont

FONTS = '/mnt/skills/examples/canvas-design/canvas-fonts'
F_DISPLAY = os.path.join(FONTS, 'InstrumentSans-Bold.ttf')   # stands in for Archivo
F_MONO    = os.path.join(FONTS, 'IBMPlexMono-Regular.ttf')
F_MONO_B  = os.path.join(FONTS, 'IBMPlexMono-Bold.ttf')

PAPER   = (233, 237, 241)
INK     = (15,  29,  40)
NAVY    = (34,  56,  74)
ACCENT  = (43,  78, 199)
YELLOW  = (245, 213, 71)
LINE    = (201, 212, 220)
LINE_STRONG = (165, 180, 191)
MUTED   = (86, 104, 117)

BRIEF = re.compile(
    r'<!--\s*IMAGE BRIEF:\s*(?P<file>[\w\-.]+)\s*\((?P<dims>[^)]+)\)'
    r'(?P<body>.*?)-->\s*<img\s+src="(?P<src>[^"]+)"',
    re.S)


def subject_of(body):
    m = re.search(r'Subject:\s*(.*?)(?=\s+(?:Composition|Mood|Colours|Colors):|$)',
                  body, re.S)
    text = m.group(1) if m else body
    return re.sub(r'\s+', ' ', text).strip().rstrip('.')


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, xy, text, font, fill, track):
    """Draw text with manual letterspacing (PIL has no tracking)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def make(path, w, h, filename, subject):
    img = Image.new('RGB', (w, h), PAPER)
    d = ImageDraw.Draw(img)

    # --- drafting grid -------------------------------------------------
    minor, major = 64, 160
    faint = tuple(round(p + (l - p) * 0.45) for p, l in zip(PAPER, LINE))
    for x in range(0, w, minor):
        d.line([(x, 0), (x, h)], fill=faint)
    for y in range(0, h, minor):
        d.line([(0, y), (w, y)], fill=faint)
    for x in range(0, w, major):
        d.line([(x, 0), (x, h)], fill=LINE)
    for y in range(0, h, major):
        d.line([(0, y), (w, y)], fill=LINE)

    m = max(24, int(w * 0.042))
    d.rectangle([m, m, w - m - 1, h - m - 1], outline=LINE_STRONG)

    # corner crop marks
    t = max(10, int(w * 0.018))
    for cx, cy, sx, sy in ((m, m, 1, 1), (w - m - 1, m, -1, 1),
                           (m, h - m - 1, 1, -1), (w - m - 1, h - m - 1, -1, -1)):
        d.line([(cx, cy), (cx + t * sx, cy)], fill=NAVY, width=2)
        d.line([(cx, cy), (cx, cy + t * sy)], fill=NAVY, width=2)

    s = w / 1200.0
    pad = m + max(16, int(28 * s))
    f_label = ImageFont.truetype(F_MONO_B, max(10, int(13 * s)))
    f_file  = ImageFont.truetype(F_MONO,   max(10, int(14 * s)))
    f_sub   = ImageFont.truetype(F_DISPLAY, max(15, int(40 * s)))

    # --- eyebrow -------------------------------------------------------
    sq = max(7, int(11 * s))
    ey = pad
    d.rectangle([pad, ey + int(2 * s), pad + sq, ey + sq + int(2 * s)], fill=ACCENT)
    tracked(d, (pad + sq + int(11 * s), ey), 'IMAGE PLACEHOLDER',
            f_label, NAVY, max(1.0, 2.0 * s))

    # --- subject brief, set as the focal block -------------------------
    avail = w - pad * 2
    lines = wrap(d, subject, f_sub, avail)[:4]
    lh = f_sub.size * 1.26
    block_h = lh * len(lines)
    ty = (h - block_h) / 2 + int(10 * s)

    d.line([(pad, ty - int(26 * s)), (pad + int(78 * s), ty - int(26 * s))],
           fill=YELLOW, width=max(3, int(5 * s)))
    for i, ln in enumerate(lines):
        d.text((pad, ty + i * lh), ln, font=f_sub, fill=NAVY)

    # --- footer line ---------------------------------------------------
    by = h - pad - f_file.size
    d.text((pad, by), filename, font=f_file, fill=ACCENT)
    dim = '%d x %d' % (w, h)
    d.text((w - pad - d.textlength(dim, font=f_file), by), dim,
           font=f_file, fill=MUTED)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'JPEG', quality=82, optimize=True, subsampling=0)
    return os.path.getsize(path)


def main():
    seen, total = {}, 0
    for f in sorted(glob.glob('posts/*.html')) + ['index.html']:
        base = os.path.dirname(f) or '.'
        src_html = io.open(f, encoding='utf-8').read()
        for mt in BRIEF.finditer(src_html):
            path = os.path.normpath(os.path.join(base, mt.group('src')))
            if path in seen:
                continue
            w, h = (int(v) for v in mt.group('dims').lower().split('x'))
            total += make(path, w, h, mt.group('file'), subject_of(mt.group('body')))
            seen[path] = True
    print('%d placeholder images written, %.1f MB total'
          % (len(seen), total / 1048576.0))


if __name__ == '__main__':
    main()
