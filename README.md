# Health Wellness

A static health & wellness blog. Plain HTML5, CSS3 and vanilla JS — no frameworks,
no build step, no npm. Deploys by drag-and-drop to Netlify Drop, Hostinger file
manager, Cloudflare Pages or any static host.

## ⚠️ There is no templating engine — these blocks are hand-copied

Four blocks are duplicated byte-for-byte into every HTML file. **If you edit one,
edit them all**, or pages will drift out of sync:

| Block | Marked by |
|---|---|
| Header + nav | `<!-- ===== SHARED HEADER — keep identical across all pages ===== -->` |
| Mobile nav | inside the header block |
| Footer + medical disclaimer | `<!-- ===== SHARED FOOTER — keep identical across all pages ===== -->` |
| `<head>` font + CSS + JS links | top of each file |

The only difference between copies is **link depth**:

- Root pages (`index.html`, `about.html`, …) use `assets/…` and `posts/…`
- `/posts/*` and `/categories/*` use `../assets/…` and `../categories/…`

There is a checker for this — run it after any header/footer edit:

```sh
sh tools/check-sync.sh
```

## Retheming

Every colour, font, space and container width is a CSS custom property in the
`:root` block at the top of `assets/css/style.css`. Change it there and the whole
site follows. Nothing downstream hardcodes a hex value.

## Before you launch — checklist

- [ ] Replace `https://healthwellness.com` with your real domain everywhere
      (`grep -rl healthwellness.com .`) — it appears in canonical tags, Open Graph
      URLs, JSON-LD and `sitemap.xml`.
- [ ] Generate the images listed in `image-briefs.md` and drop them into
      `assets/images/<post-slug>/`.
- [ ] Point the email signup `<form action>` at a real service, then delete the
      `data-placeholder` attribute (and the block in `main.js` that intercepts it).
- [ ] Point the contact form at Formspree / Basin / Netlify Forms.
- [ ] Inject your AdSense or Monetag script into the `.ad-slot` divs. They are
      empty containers with `data-ad-slot` names — no ad network code is hardcoded.
- [ ] Re-check every external citation link still resolves before publishing.
- [ ] Submit `sitemap.xml` in Google Search Console.

## Structure

```
/                     index, about, contact, privacy-policy, medical-disclaimer, 404
/assets/css/          style.css — the whole design system
/assets/js/           main.js — nav, TOC highlight, share, progress bar
/assets/images/       one folder per post slug
/categories/          5 pillar landing pages
/posts/               100 post files
content-map.md        the 100-post plan
image-briefs.md       master checklist of every image the site needs
```

## Editorial rules (YMYL)

This is health content, which Google holds to stricter "Your Money or Your Life"
standards. Every post must keep:

- An author byline that is **honest about credentials** — Sam Reyes is explicitly
  not a doctor, physiotherapist or certified coach.
- Hedged language. "Some evidence suggests", "may help with" — never "cures",
  "guarantees" or "eliminates".
- Real, checkable citations. Never invent a study, a journal or a statistic.
- A `Last updated` date in the byline and in `dateModified` in the JSON-LD.
- The medical disclaimer in the footer, linked from every page.
