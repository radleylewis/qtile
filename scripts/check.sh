#!/bin/sh
# Quick pre-reload check: catches "config won't load" mistakes, not runtime behaviour
# (locking, suspend, hotplug still need a real test).
# Usage: sh ~/.config/qtile/scripts/check.sh

cd "$(dirname "$0")/.." || exit 1
fail=0

step() {
	printf '%-28s' "$1"
	shift
	if out=$("$@" 2>&1); then
		echo ok
	else
		echo FAIL
		echo "$out" | tail -15
		fail=1
	fi
}

step "qtile check" qtile check -c config.py
step "python syntax" python3 -m py_compile config.py top_bar.py assets/*.py utils/*.py scripts/*.py
# importing config.py pulls in every module, so this catches import errors too
step "config import (cheatsheet)" python3 scripts/cheatsheet.py --plain
for f in scripts/*.sh; do
	step "sh syntax $(basename "$f")" sh -n "$f"
done

[ "$fail" -eq 0 ] && echo "all checks passed" || echo "checks FAILED"
exit "$fail"
