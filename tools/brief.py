# -*- coding: utf-8 -*-
"""Helper for the in-file image briefs. Keeps the palette line identical."""
PALETTE = ("cool drafting ground (#E9EDF1), navy (#22384A), cobalt (#2B4EC7),\n"
           "             surveyor's yellow used sparingly (#F5D547).")

def hero(slug, subject, composition, mood):
    return ("        <!-- IMAGE BRIEF: {s}-hero.jpg (1200x630)\n"
            "             Subject: {su}\n"
            "             Composition: {c}\n"
            "             Mood: {m}\n"
            "             Colours: {p} -->").format(
                s=slug, su=subject, c=composition, m=mood, p=PALETTE)

def inline(slug, n, subject, composition, mood, w=1200, h=800):
    return ("          <!-- IMAGE BRIEF: {s}-{n:02d}.jpg ({w}x{h})\n"
            "               Subject: {su}\n"
            "               Composition: {c}\n"
            "               Mood: {m}\n"
            "               Colours: {p} -->").format(
                s=slug, n=n, w=w, h=h, su=subject, c=composition, m=mood, p=PALETTE)

def figure(slug, n, alt, caption, subject, composition, mood, w=1200, h=800):
    return u"""        <figure>
{brief}
          <img src="../assets/images/{s}/{s}-{n:02d}.jpg"
               alt="{alt}"
               width="{w}" height="{h}" loading="lazy">
          <figcaption>{cap}</figcaption>
        </figure>""".format(brief=inline(slug, n, subject, composition, mood, w, h),
                            s=slug, n=n, alt=alt, cap=caption, w=w, h=h)
