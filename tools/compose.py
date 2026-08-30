# -*- coding: utf-8 -*-
"""Compose finished blueprint diagrams from posed figures.

Layouts:
  two_panel  start -> finish, the way a form guide shows a movement
  one_panel  a single position with a cue callout
  grid_panel a week / plan grid, for scheduling and habit posts
  space_plan an overhead floor plan, for the small-space posts
"""
import figures as F

W, H = 1200, 630


def _cues(items, y0=252):
    """Two or three short form cues down the left, numbered like a spec sheet."""
    o = []
    for i, t in enumerate(items[:3]):
        y = y0 + i * 62
        o.append('<rect x="84" y="%d" width="26" height="26" fill="%s"/>' % (y - 19, F.ACCENT))
        o.append(F.label(91, y, str(i + 1), size=17, weight=700, colour='#FFFFFF', mono=True))
        o.append(F.label(126, y, t, size=20, weight=500, colour=F.NAVY))
    return o


def _chrome(title, eyebrow, caption, w=None, h=None):
    w, h = w or W, h or H
    o = [F.grid(w, h), F.frame(w, h)]
    o.append(F.eyebrow(84, 104, eyebrow))
    # title wraps to two lines at a rough character count
    words, lines, cur = title.split(), [], ''
    for w in words:
        if len(cur + ' ' + w) <= 40 or not cur:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    for i, ln in enumerate(lines[:2]):
        o.append(F.label(84, 158 + i * 44, ln, size=34, weight=700))
    o.append('<rect x="84" y="%d" width="76" height="5" fill="%s"/>'
             % (158 + min(len(lines), 2) * 44 - 24, F.YELLOW))
    if caption:
        o.append(F.label(84, h - 44, caption, size=20, weight=400, colour=F.MUTED))
    return o


def two_panel(title, eyebrow, caption, pose_a, pose_b, label_a, label_b, cues=()):
    o = _chrome(title, eyebrow, caption)
    bw, gap = 330, 96
    x0 = (W - (2 * bw + gap)) / 2
    bb = F.union_bbox([pose_a, pose_b])        # one scale, one ground, both panels
    for i, (pose, lab) in enumerate(((pose_a, label_a), (pose_b, label_b))):
        x = x0 + i * (bw + gap)
        box = (x, 268, bw, 250)
        o.append(F.support(box, pose, bb, 10))
        o.append(F.figure(pose, box, stroke=8, bb=bb))
        o.append(F.label(x + bw / 2, 524, lab, size=19, weight=700,
                         colour=F.NAVY, anchor='middle', mono=True))
    o.append(F.arrow(x0 + bw + 20, 392, x0 + bw + gap - 20, 392, w=5))
    return F.svg(W, H, '\n'.join(o))


def one_panel(title, eyebrow, caption, pose, note='', cues=()):
    o = _chrome(title, eyebrow, caption)
    box = ((W - 520) / 2, 250, 520, 280)
    o.append(F.support(box, pose, None, 30))
    o.append(F.figure(pose, box, stroke=9))
    if note:
        o.append(F.label(W / 2, 546, note, size=19, weight=700, colour=F.NAVY,
                         anchor='middle', mono=True))
    return F.svg(W, H, '\n'.join(o))


DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']


def week_grid(title, eyebrow, caption, sessions=3, cues=(), note='', w=None, h=None):
    """A training week as a strip of day cells, filled cells being sessions.

    Used for the scheduling and habit posts, where a posed figure says nothing.
    Three sessions is the default because it is what the guidance the site cites
    actually asks for — the post's own headings carry the specifics.
    """
    w, h = w or W, h or H
    o = _chrome(title, eyebrow, caption, w, h)
    pat = {1: [2], 2: [1, 4], 3: [0, 2, 4], 4: [0, 1, 3, 5], 5: [0, 1, 2, 4, 5],
           6: [0, 1, 2, 3, 4, 5], 7: [0, 1, 2, 3, 4, 5, 6]}.get(sessions, [0, 2, 4])
    cw, ch, gap = 74, 92, 12
    x0 = (w - (7 * cw + 6 * gap)) / 2
    y0 = 380 if h > 700 else 290
    for i, d in enumerate(DAYS):
        x = x0 + i * (cw + gap)
        on = i in pat
        o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" '
                 'stroke-width="%d"/>' % (x, y0, cw, ch, F.ACCENT if on else '#FFFFFF',
                                          F.ACCENT if on else F.LINE_STRONG, 2 if on else 1))
        if on:
            o.append('<rect x="%d" y="%d" width="%d" height="6" fill="%s"/>'
                     % (x + 16, y0 + ch - 26, cw - 32, F.YELLOW))
        o.append(F.label(x + cw / 2, y0 + ch + 30, d, size=15, weight=700, mono=True,
                         colour=F.NAVY if on else F.MUTED, anchor='middle'))
    o.append(F.label(x0, y0 - 22, '%d SESSIONS A WEEK' % sessions, size=16,
                     weight=700, mono=True, colour=F.ACCENT))
    if note:
        o.append(F.label(w - 72, y0 + ch + 76, note, size=18, weight=500,
                         colour=F.MUTED, anchor='end'))
    return F.svg(w, h, '\n'.join(o))


def three_panel(title, eyebrow, caption, items, w=1200, h=800):
    """Three positions compared — used to show one correct form against faults."""
    o = _chrome(title, eyebrow, '', w, h)
    o.append(F.label(84, 232, caption, size=20, weight=400, colour=F.MUTED))
    bb = F.union_bbox([p for p, _, _ in items])
    bw, gap = 300, 42
    x0 = (w - (3 * bw + 2 * gap)) / 2
    for i, (pose, lab, good) in enumerate(items):
        x = x0 + i * (bw + gap)
        box = (x, 300, bw, 250)
        o.append('<rect x="%.0f" y="%d" width="%d" height="%d" fill="#FFFFFF" stroke="%s" '
                 'stroke-width="%d"/>' % (x, 288, bw, 300, F.ACCENT if good else F.LINE_STRONG,
                                          3 if good else 1))
        o.append(F.support(box, pose, bb, 6))
        o.append(F.figure(pose, box, stroke=8, bb=bb))
        o.append('<rect x="%.0f" y="%d" width="%d" height="7" fill="%s"/>'
                 % (x + bw / 2 - 30, 616, 60, F.ACCENT if good else F.YELLOW))
        o.append(F.label(x + bw / 2, 660, lab, size=19, weight=700, mono=True,
                         colour=F.NAVY if good else F.MUTED, anchor='middle'))
    return F.svg(w, h, '\n'.join(o))


def exercise_grid(title, eyebrow, caption, items, w=1200, h=800):
    """A numbered 3x2 board of the session's movements, in order."""
    o = _chrome(title, eyebrow, '', w, h)
    o.append(F.label(84, 226, caption, size=20, weight=400, colour=F.MUTED))
    bb = F.union_bbox([p for p, _ in items])
    cw, chh, gx, gy = 330, 196, 24, 52
    x0 = (w - (3 * cw + 2 * gx)) / 2
    y0 = 268
    for i, (pose, lab) in enumerate(items[:6]):
        cx = x0 + (i % 3) * (cw + gx)
        cy = y0 + (i // 3) * (chh + gy)
        o.append('<rect x="%.0f" y="%.0f" width="%d" height="%d" fill="#FFFFFF" stroke="%s"/>'
                 % (cx, cy, cw, chh, F.LINE))
        box = (cx + 60, cy + 16, cw - 120, chh - 32)
        o.append(F.support(box, pose, bb, 8))
        o.append(F.figure(pose, box, stroke=6, bb=bb))
        o.append('<rect x="%.0f" y="%.0f" width="30" height="30" fill="%s"/>' % (cx, cy, F.ACCENT))
        o.append(F.label(cx + 9, cy + 22, str(i + 1), size=18, weight=700,
                         colour='#FFFFFF', mono=True))
        o.append(F.label(cx + cw / 2, cy + chh + 30, lab, size=18, weight=600,
                         colour=F.NAVY, anchor='middle'))
    return F.svg(w, h, '\n'.join(o))


def cover(pose_a, pose_b=None, w=1200, h=900):
    """A text-free card image, for the magazine grid.

    The hero diagrams carry their own title and caption, which makes them
    unusable behind an overlaid headline. This is the same artwork with every
    word stripped out, so the card can put its own text on top.
    """
    o = [F.grid(w, h), F.frame(w, h, m=34)]
    if pose_b:
        bb = F.union_bbox([pose_a, pose_b])
        bw, gap = int(w * 0.40), int(w * 0.04)
        x0 = (w - (2 * bw + gap)) / 2
        for i, pose in enumerate((pose_a, pose_b)):
            box = (x0 + i * (bw + gap), h * 0.10, bw, h * 0.78)
            o.append(F.support(box, pose, bb, 10))
            o.append(F.figure(pose, box, stroke=13, bb=bb))
    else:
        box = (w * 0.10, h * 0.08, w * 0.80, h * 0.84)
        o.append(F.support(box, pose_a, None, 24))
        o.append(F.figure(pose_a, box, stroke=15))
    return F.svg(w, h, '\n'.join(o))
