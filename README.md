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

## Search

The site is static, so search runs in the browser against a prebuilt index.

`assets/search-index.json` (~61 KB, roughly 15 KB gzipped) holds each post's
title, standfirst, section headings and target keyword. It is fetched lazily the
first time search is opened, so a normal page view never pays for it. Body text
is deliberately excluded — 340,000 words would be several megabytes, and titles
and headings already cover what people type.

Matching requires **every** query token to appear somewhere, so "quiet
apartment" will not return a post that only mentions apartments. Field weights
order the results: title, then keyword, then heading, then standfirst. Pillar
guides break ties upward.

- **Open it** with the magnifying glass, `Ctrl`/`Cmd`+`K`, or `/`
- **Navigate** with arrow keys, `Enter` to open the top hit, `Esc` to close

`search.html` is the fallback and works with no JavaScript at all: it lists
every guide grouped by section. With JavaScript the same page becomes a live
filter and the browse list hides once you type.

One deployment note: browsers block `fetch` of a local JSON file over
`file://`, so search will not work if you open the site straight off disk. It
is fine on any real server. The failure is handled — the panel offers the
browse page instead of failing silently.

Rebuild the index after editing posts:

```
python3 tools/build_search_index.py
python3 tools/build_search_page.py
```

## Images

Every photograph is sourced from [Openverse](https://openverse.org/) and
Wikimedia Commons under licences that permit commercial use and modification,
then cropped to two sizes: a `-hero.jpg` (1200×630, also the Open Graph share
image) and a `-cover.jpg` (1200×900) used behind headlines on the front-page
mosaic and category thumbnails.

**Attribution is a licence condition, not a courtesy.** Images under CC-BY or
CC-BY-SA name their photographer in a credit line under the picture and in
`credits.html`, which is generated from the same manifest the images came from
so it cannot drift. Re-run `python3 tools/build_credits_page.py` after changing
any image. CC0 and public-domain images need no attribution but are listed too.

### Why two sources

Openverse matches on titles, which fails badly on everyday English words —
"squat" returns squat lobsters, "push up" returns starfish, "dumbbell" returns
the Dumbbell Nebula. Its queries here are long and specific for that reason, and
a junk-title filter drops manuscripts, museum objects and clipart.

Wikimedia Commons *categories* are curated by people, so `Category:Push-ups`
actually contains push-ups. That is the only source that reliably covers
exercise-specific imagery, so it fills the gaps Openverse cannot.

### Rebuilding the set

```
python3 tools/fetch_photos.py      # Openverse sweep -> tools/photo-pool.json
python3 tools/topup_photos.py      # top up thin categories, merges into the pool
python3 tools/commons_photos.py    # Commons categories, merges into the pool
python3 tools/apply_photos.py      # assign, crop to hero + cover
python3 tools/photo_captions.py    # alt text and credit lines
python3 tools/build_credits_page.py
```

The downloaded originals in `tools/photos/` are gitignored working files —
every source URL lives in `photo-pool.json`, so `fetch_photos.py` can restore
them.

### What is still drawn rather than photographed

Three in-content diagrams are still generated line art, because a photograph
cannot do their job: the push-up form comparison (correct against two faults),
the six-exercise session board, and the training-week grid. `tools/figures.py`
and `tools/make_images.py` still build those, and can redraw the whole set if
you ever want the diagrams back.

## The front page

The site is laid out as a news magazine rather than a blog:

- **Ticker** — a breaking-news strip carrying the five pillar guides
- **Masthead** — brand, primary nav, RSS/contact/search
- **Utility bar** — secondary links and a dateline, written by JS so a static
  file never shows a stale date
- **Mosaic** — one lead story plus a 2×2 of seconds, every cell an image tile
  with a category badge and an overlaid headline
- **Section tabs** — headings as a filled tab sitting on a rule, in the
  section's colour
- **Strip** — a four-across thumbnail row

The five pillar colours do the sorting, which is how a magazine grid signals
section. Each card image is a text-free **cover** variant of the post's diagram;
the hero versions carry their own titles and cannot take an overlaid headline.

The ticker, masthead and utility bar are hand-copied into all 111 files like the
other shared blocks — `python3 tools/magazine_chrome.py` rewrites them, and
`tools/check-sync.sh` fails if any page is missing one.

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
