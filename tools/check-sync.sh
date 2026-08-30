#!/bin/sh
# Verifies the hand-copied header/footer blocks are present and consistent
# across every HTML file. Run after editing either shared block.
set -u

fail=0
files=$(find . -name '*.html' -not -path './.git/*' | sort)
total=$(printf '%s\n' "$files" | grep -c . || true)

echo "Checking $total HTML files..."
echo

for f in $files; do
  msg=""
  grep -q 'SHARED HEADER' "$f" || msg="$msg  missing SHARED HEADER block\n"
  grep -q 'SHARED FOOTER' "$f" || msg="$msg  missing SHARED FOOTER block\n"
  grep -q 'class="ticker"' "$f" || msg="$msg  missing ticker band\n"
  grep -q 'class="utility-bar"' "$f" || msg="$msg  missing utility bar\n"
  grep -q 'data-today' "$f" || msg="$msg  missing dateline\n"
  grep -q 'search.js' "$f" || msg="$msg  missing search.js\n"
  grep -q 'data-search' "$f" || msg="$msg  missing search button\n"
  grep -q 'medical-disclaimer.html' "$f" || msg="$msg  missing medical disclaimer link\n"
  grep -q 'style.css' "$f" || msg="$msg  missing stylesheet link\n"
  grep -q 'main.js' "$f" || msg="$msg  missing main.js\n"
  grep -q 'config.js' "$f" || msg="$msg  missing config.js\n"
  grep -q 'forms.js' "$f" || msg="$msg  missing forms.js\n"
  grep -q 'ads.js' "$f" || msg="$msg  missing ads.js\n"
  # config.js must load before main.js so SITE_CONFIG exists when scripts run
  if [ "$(grep -n 'assets/js/config.js' "$f" | head -1 | cut -d: -f1)" -gt \
       "$(grep -n 'assets/js/main.js' "$f" | head -1 | cut -d: -f1)" ]; then
    msg="$msg  config.js must be loaded before main.js\n"
  fi
  grep -q '<meta name="viewport"' "$f" || msg="$msg  missing viewport meta\n"
  grep -q 'rel="canonical"' "$f" || msg="$msg  missing canonical tag\n"
  grep -q 'og:title' "$f" || msg="$msg  missing Open Graph tags\n"

  # Link depth must match directory depth
  # every post and category page must declare which of the five section
  # colours it uses, or it silently falls back to the house accent
  case "$f" in
    ./posts/*|./categories/*)
      grep -q '<body data-pillar="' "$f" || msg="$msg  missing data-pillar on <body>\n" ;;
  esac

  case "$f" in
    ./posts/*|./categories/*)
      grep -q 'href="../assets/css/style.css"' "$f" || msg="$msg  wrong CSS path (needs ../)\n"
      grep -q 'src="../assets/js/config.js"' "$f" || msg="$msg  wrong config.js path (needs ../)\n" ;;
    *)
      grep -q 'href="assets/css/style.css"' "$f" || msg="$msg  wrong CSS path (needs no ../)\n"
      grep -q 'src="assets/js/config.js"' "$f" || msg="$msg  wrong config.js path (needs no ../)\n" ;;
  esac

  if [ -n "$msg" ]; then
    echo "FAIL $f"
    printf "$msg"
    fail=$((fail+1))
  fi
done

echo
if [ "$fail" -eq 0 ]; then
  echo "OK — all $total files consistent."
else
  echo "$fail file(s) need attention."
  exit 1
fi
