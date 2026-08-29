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
  grep -q 'medical-disclaimer.html' "$f" || msg="$msg  missing medical disclaimer link\n"
  grep -q 'style.css' "$f" || msg="$msg  missing stylesheet link\n"
  grep -q 'main.js' "$f" || msg="$msg  missing main.js\n"
  grep -q '<meta name="viewport"' "$f" || msg="$msg  missing viewport meta\n"
  grep -q 'rel="canonical"' "$f" || msg="$msg  missing canonical tag\n"
  grep -q 'og:title' "$f" || msg="$msg  missing Open Graph tags\n"

  # Link depth must match directory depth
  case "$f" in
    ./posts/*|./categories/*)
      grep -q 'href="../assets/css/style.css"' "$f" || msg="$msg  wrong CSS path (needs ../)\n" ;;
    *)
      grep -q 'href="assets/css/style.css"' "$f" || msg="$msg  wrong CSS path (needs no ../)\n" ;;
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
