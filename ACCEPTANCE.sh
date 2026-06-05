#!/usr/bin/env bash
set -euo pipefail

REPO="C:/Users/dasha/Projects/erdos-straus-solver"
cd "$REPO"

echo "=== KAGGLE PUBLISH CI GATES ==="

# 1. COMPILE: all modified scripts pass py_compile
python3 -m py_compile export_to_jsonl.py
python3 -m py_compile generate_dashboard_json.py
python3 -m py_compile erdos_watchdog.py
python3 -m py_compile master_orchestrator.py
echo "PASS: all scripts compile"

# 2. PATH: verify no hardcoded ~/Projects/erdos-straus references remain
HARDCODED=$(grep -r "~/Projects/erdos-straus[^/]" . --include="*.py" -l 2>/dev/null || true)
if [ -n "$HARDCODED" ]; then
  echo "FAIL: hardcoded paths found in: $HARDCODED"
  exit 1
fi
echo "PASS: no hardcoded home paths"

# 3. KAGGLE METADATA: validate kernel-metadata.json has required fields
python3 -c "
import json
with open('kernel-metadata.json') as f:
    m = json.load(f)
required = ['id', 'title', 'code_file', 'language', 'kernel_type', 'is_private', 'enable_gpu']
for r in required:
    assert r in m, f'missing required field: {r}'
assert 'dataset_sources' in m, 'missing dataset_sources for auto-mount'
assert m['code_file'].endswith('.py'), 'code_file must be a .py script'
print('PASS: kernel-metadata.json valid')
"

# 4. KAGGLE DATASET README: must exist
if [ ! -f "kaggle_dataset/README.md" ]; then
  echo "FAIL: kaggle_dataset/README.md missing"
  exit 1
fi
echo "PASS: kaggle_dataset/README.md exists"

# 5. JSONL VALIDITY: export must produce valid JSONL if file exists
if [ -f "kaggle_dataset/erdos_solutions.jsonl" ]; then
  python3 -c "
import json
with open('kaggle_dataset/erdos_solutions.jsonl') as f:
    for i, line in enumerate(f):
        json.loads(line)
        if i >= 100: break
print('PASS: JSONL valid (first 100 lines)')
"
else
  echo "SKIP: kaggle_dataset/erdos_solutions.jsonl not yet generated"
fi

# 6. VINCULUM: sample 10 records and verify integer triple sum = 4/n
python3 -c "
import json, sys
from pathlib import Path
p = Path('kaggle_dataset/erdos_solutions.jsonl')
if not p.exists():
    print('SKIP: file not yet generated')
    sys.exit(0)
with open(p) as f:
    for i, line in enumerate(f):
        if i >= 10: break
        d = json.loads(line)
        n = d['n']
        x, y, z = d['triple']
        lhs = 4.0 / n
        rhs = 1.0/x + 1.0/y + 1.0/z
        assert abs(lhs - rhs) < 1e-9, f'breach at n={n}: {lhs} != {rhs}'
print('PASS: 10 sampled solutions satisfy 4/n = 1/x+1/y+1/z')
"

echo "ALL GATES PASSED"
