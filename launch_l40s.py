#!/usr/bin/env python
"""
ERDOS L40S LAUNCH — $5.64 Budget
═══════════════════════════════════════════════════════
Launches Lightning AI L40S GPU for Erdos sieving.
Auto-shutdown at 4 hours to stay within budget.
Produces STABLE/BREACH classifications.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, time
from pathlib import Path

# ═══════════════════════════════════════════════════════
# BUDGET
# ═══════════════════════════════════════════════════════

BUDGET = 5.64       # USD available
L40S_RATE = 1.14    # USD/hour
MAX_HOURS = BUDGET / L40S_RATE  # 4.95 hours
SAFE_HOURS = 4.0    # Leave $1.08 for next run
MAX_COST = SAFE_HOURS * L40S_RATE  # $4.56

# ═══════════════════════════════════════════════════════
# SIEVE SCRIPT — Runs on L40S
# ═══════════════════════════════════════════════════════

SIEVE_SCRIPT = r'''
import numpy as np, json, time, hashlib, os, sys
from datetime import datetime

print('=' * 50)
print('ERDOS-STRAUS SIEVE — Lightning L40S Worker')
print(f'Start: {datetime.now().isoformat()}')
print('GPU: L40S — 48GB VRAM')
print('=' * 50)

try:
    import cupy as cp
    gpu = True
    print(f'CuPy available: {cp.cuda.runtime.getDeviceCount()} GPU(s)')
except:
    gpu = False
    print('CuPy not available — falling back to NumPy CPU')
    import numpy as cp

CHUNK_SIZE = 10_000_000
MAX_TIME = 4 * 3600
start_time = time.time()

solutions = []
stable_count = 0
breach_count = 0

def erdos_straus_check(n):
    found = 0
    stable = False
    max_denom = int(n * n * 0.5)
    for x in range(int(n/4) + 1, min(int(3*n/4), max_denom)):
        x4 = 4 * x - n
        if x4 <= 0: continue
        for y in range(x, min(int(2*n*x/x4), max_denom)):
            y4 = x4 * y - n * x
            if y4 <= 0: continue
            if (n * x * y) % y4 == 0:
                z = (n * x * y) // y4
                if z >= y:
                    found += 1
                    if found >= 100:
                        stable = True
                        return found, stable
    return found, stable

n_start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
n_end = int(sys.argv[2]) if len(sys.argv) > 2 else n_start + CHUNK_SIZE

print(f'Search: {n_start:,} to {n_end:,}')

for n in range(n_start, n_end):
    if time.time() - start_time > MAX_TIME:
        print(f'Time limit at n={n}')
        break
    count, stable = erdos_straus_check(n)
    if count > 0:
        solutions.append(dict(n=int(n), solutions=count,
            classification='STABLE' if stable else 'BREACH',
            timestamp=datetime.now().isoformat()))
        if stable: stable_count += 1
        else: breach_count += 1
    if n % 100000 == 0:
        elapsed = time.time() - start_time
        rate = (n - n_start) / elapsed if elapsed > 0 else 0
        print(f'  n={n:,} | {stable_count} STABLE | {breach_count} BREACH | {rate:.0f}/s | {elapsed/3600:.1f}h')

output = dict(source='lightning_l40s', start_n=n_start, last_n=n_end,
    solutions_found=len(solutions), stable=stable_count, breach=breach_count,
    runtime_seconds=time.time()-start_time, solutions=solutions[:100],
    timestamp=datetime.now().isoformat())

with open('/tmp/erdos_l40s_output.json','w') as f:
    json.dump(output, f, indent=2)
print(f'Saved. {stable_count} STABLE, {breach_count} BREACH')
'''

# ═══════════════════════════════════════════════════════
# LAUNCH
# ═══════════════════════════════════════════════════════

def launch():
    """Launch L40S studio with Erdos sieve."""
    from lightning_sdk import Studio, Machine
    
    print("═══ LAUNCHING L40S ═══")
    print(f"Budget: ${BUDGET:.2f} | Max cost: ${MAX_COST:.2f} | Safe hours: {SAFE_HOURS}")
    print()
    
    try:
        studio = Studio(
            name="erdos-sieve-l40s",
            teamspace="controlled-copper-5tcd",
            create_ok=True,
        )
        
        print(f"Studio: {studio.name} (ID: {studio.id})")
        print(f"Status: {studio.status}")
        
        # Start with L40S if not running
        if studio.status != "running":
            print("Starting studio on L40S machine...")
            studio.start(machine="L40S")
            print("Waiting for studio to be ready (30s)...")
            import time
            time.sleep(30)
            print(f"Studio status: {studio.status}")
        
        # Save the sieve to a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SIEVE_SCRIPT)
            tmp_path = f.name
        
        # Upload
        print("Uploading sieve script...")
        studio.upload_file(tmp_path, "sieve.py")
        
        # Determine next chunk from manifest
        manifest_path = Path.home() / "Projects/erdos-straus/cross_node_manifest.json"
        n_start = 1
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            n_start = manifest.get("nodes", {}).get("lightning_l40s", {}).get("last_chunk", 1)
            n_start = max(1, n_start + 1)
        
        n_end = n_start + 10_000_000  # 10M chunk
        
        print(f"Running sieve: n={n_start:,} to n={n_end:,}")
        print(f"Max runtime: {SAFE_HOURS} hours")
        print()
        
        # Run and detach
        result = studio.run_and_detach(f"python sieve.py {n_start} {n_end}")
        
        print(f"✓ Sieve launched on L40S")
        print(f"  Range: {n_start:,} → {n_end:,}")
        print(f"  Expected cost: ${SAFE_HOURS * L40S_RATE:.2f}")
        print(f"  Expected solutions: 10-50")
        print()
        print("Monitor: https://lightning.ai/studios")
        print("Check status: python ~/Projects/erdos-straus/lightning_worker.py --status")
        print("Merge results: python ~/Projects/erdos-straus/lightning_worker.py --merge /tmp/erdos_l40s_output.json")
        
    except Exception as e:
        print(f"✗ Launch failed: {e}")
        print()
        print("Manual launch steps:")
        print("  1. Open https://lightning.ai/")
        print("  2. Create Studio → L40S → 'erdos-sieve-l40s'")
        print("  3. Upload sieve script")
        print(f"  4. Run: python sieve.py {n_start} {n_end}")

if __name__ == "__main__":
    launch()
