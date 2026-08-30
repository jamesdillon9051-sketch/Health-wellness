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

Everything that could be done without an account of yours has been done. What is
left needs a value only you have — each is one edit, not a hunt through 111 files.

- [ ] **Point it at your domain.** One command rewrites all 1,279 occurrences
      across canonical tags, Open Graph and Twitter URLs, JSON-LD `@id` fields,
      `sitemap.xml` and `robots.txt`:

      python3 tools/set_domain.py https://yourdomain.com

      Add `--dry` to preview. Re-runnable if you ever move domains.

- [ ] **Connect the forms.** Create two forms at
      [formspree.io](https://formspree.io) (free tier is fine), then paste the
      two IDs into `assets/js/config.js`. Both the contact form and all 108
      signup blocks pick them up — no per-page editing. Until you do, both say
      so on screen rather than silently dropping what someone typed.

- [ ] **Switch on ads** (optional). Put your AdSense publisher ID and four slot
      IDs into the same `config.js`. Any zone you leave empty renders nothing at
      all, so an unmonetised site still looks finished. `?ads=debug` on any URL
      shows the slots while you are designing.

- [ ] **Replace the placeholder images.** All 103 are generated and in place, so
      the site renders complete today. Each is stamped with its own brief;
      `image-briefs.md` lists every one. Overwrite a file with the real
      photograph at the same path — no HTML edit needed.

- [ ] **Re-read the citations.** `python3 tools/citecheck.py` prints all 275
      footnoted claims beside their sources and flags pairings worth a second
      look. It currently flags none, but that is triage, not proof — on a health
      site the human read is the one that counts.

- [ ] **Submit the sitemap.** Verify the domain in
      [Google Search Console](https://search.google.com/search-console), then
      submit `sitemap.xml` (110 URLs, validated). Bing Webmaster Tools accepts
      the same file.

## Tools

None of these are needed to run the site — it is plain HTML with no build step.
They exist to keep the hand-copied blocks honest.

```
tools/set_domain.py        rewrite the site's domain everywhere, in one pass
tools/make_placeholders.py regenerate the blueprint placeholder images
tools/audit.py             word counts, link minimums, JSON-LD, meta tags
tools/linkcheck.py         every internal href and #anchor resolves
tools/citecheck.py         every footnoted claim printed beside its source
tools/check-sync.sh        the four hand-copied blocks are identical everywhere
tools/build_site_files.py  regenerate sitemap.xml, robots.txt, image-briefs.md
tools/wire_services.py     re-wire config/forms/ads scripts into every page
```

## Structure

```
/                     index, about, contact, privacy-policy, medical-disclaimer, 404
/assets/css/          style.css — the whole design system
/assets/js/           config.js — THE ONE FILE YOU EDIT to connect services
                      main.js   — nav, TOC highlight, share, progress bar
                      forms.js  — contact + signup submission
                      ads.js    — fills the .ad-slot divs from config.js
/assets/images/       one folder per post slug (placeholders in place)
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
