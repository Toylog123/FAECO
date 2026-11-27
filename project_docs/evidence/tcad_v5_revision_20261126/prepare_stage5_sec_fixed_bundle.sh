#!/usr/bin/env bash
# Prepare a new Stage 5 capsule with the already validated SEC source change.
set -euo pipefail

[[ $# == 3 ]] || { echo 'Usage: prepare_stage5_sec_fixed_bundle.sh <original-bundle> <new-bundle> <fixed-prove_ibex.py>' >&2; exit 2; }
original=$(realpath -e -- "$1")
output=$(realpath -m -- "$2")
fixed=$(realpath -e -- "$3")
case "$output/" in "$original/"*) echo 'The new bundle must be outside the original.' >&2; exit 2 ;; esac
test ! -e "$output"

path=project/project_docs/evidence/tcad_ibex_20261123/prove_ibex.py
original_hash=9388a0c69c13ab2dc91352e3431ebcd5927d1884c79ed8db2b38ec0f67403e7b
fixed_hash=861d3549ea8f20f082c6b30e58e7c3bb4cf56adabd48a50f210cf749d86ddfd4
test -f "$original/$path"
test ! -L "$original/$path"
printf '%s  %s\n' "$original_hash" "$original/$path" "$fixed_hash" "$fixed" | sha256sum -c

cp -a --reflink=auto -- "$original" "$output"
cp -- "$fixed" "$output/$path"
python3 -B - "$original/FILES.sha256" "$output/FILES.sha256" "$path" "$original_hash" "$fixed_hash" <<'PY'
from pathlib import Path
import sys

old, new = map(Path, sys.argv[1:3])
path, before, after = sys.argv[3:]
original = old.read_bytes()
line = f"{before}  {path}\n".encode()
if original.count(line) != 1 or new.read_bytes() != original:
    raise ValueError("cannot bind the sole approved edit to the original file manifest")
new.write_bytes(original.replace(line, f"{after}  {path}\n".encode()))
PY

cmp -- "$original/FILES.list0" "$output/FILES.list0"
cmp -- "$original/LINKS.tsv" "$output/LINKS.tsv"
diff -u -- "$original/FILES.sha256" "$output/FILES.sha256" || [[ $? == 1 ]]
sha256sum -- "$original/FILES.sha256" "$output/FILES.sha256"
