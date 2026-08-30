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

## The colour system

The site is one warm near-white ground plus five saturated section colours.
Every page carries `data-pillar` on `<body>`, which repoints four tokens:

| token | used for |
|---|---|
| `--accent` | vivid. Large blocks and washes only |
| `--accent-deep` | buttons, links, small text. White on it is >= 4.5:1 for all five |
| `--accent-tint` | pale wash for callouts, TOC, hub headers |
| `--accent-on` | text colour that sits *on* `--accent` |

Every rule in `style.css` is written against those four, so a page reskins from
one attribute. There are two accents per pillar because white on the vivid tone
fails on amber (2.4:1) and coral (3.9:1) — anything carrying text uses
`--accent-deep`, so button text is white everywhere with no exceptions.

| section | vivid | deep | on-vivid |
|---|---|---|---|
| Bodyweight strength | `#E8483F` coral | `#C62F27` | ink |
| Quick workouts | `#0E9C8A` teal | `#0A7365` | ink |
| Small-space training | `#6B4CE0` violet | `#5C3BD6` | white |
| Minimal gear | `#E8930C` amber | `#A96504` | ink |
| Habits & recovery | `#2E9E4F` green | `#268543` | ink |

Pages belonging to no single pillar (home, about, contact, legal) use the house
indigo on `:root`. All 17 foreground/background pairings were measured against
WCAG AA; the lowest is amber-deep on paper at 4.50:1.

To retheme, edit the pillar block in `:root` — nothing else references a colour
directly. `python3 tools/set_pillar.py` re-applies the body attributes if you
add pages, and `python3 tools/make_images.py` redraws the 103 diagrams in
whatever the new colours are.

## Typography

Two families, split by role rather than by size.

| face | job |
|---|---|
| **Bricolage Grotesque** | the whole interface — headings, nav, buttons, cards, labels, tables, forms |
| **Newsreader** | prose read at length — post bodies, standfirsts, FAQ answers, sources |

A serif earns its place across 1,200–1,800 words; it does not earn one in a nav
bar. Prose gets its own scale (`--text-prose`, `--leading-prose`) because
Newsreader runs smaller and lighter than a sans at the same pixel size.

Both load from Google Fonts as variable faces — one request, roughly 150 KB
over the wire once the browser picks its subset. The diagrams are drawn in
Bricolage too, from the local font file, so images and page match.

## Section templates

Each part of the site is laid out as its own place:

- **Homepage** — the five pillars as solid colour blocks; post cards carry the
  colour of the section they belong to.
- **Category pages** — a full-bleed masthead in that section's colour, and every
  card below it themed to match.
- **Posts** — a coloured rail on the standfirst, a tinted contents panel, and
  coloured section rules.
- **Hub posts** — a tinted header block with a heavy top rule, so the ten pillar
  guides read as more substantial than the clusters hanging off them.
- **Diagrams** — each of the 103 is drawn on its own section's tinted ground.

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
