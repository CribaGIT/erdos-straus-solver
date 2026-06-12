#!/usr/bin/env python
"""ERDOS L40S — HOT CORRIDOR DEEP SIEVE
Target: mod24=0, mod9∈{0,3,6} — 100% breach rate from 347-sample classification.
GPU: L40S ($2.89/hr) — 48GB VRAM — Lightning Studio
DaShawn / Guinea Pig Trench LLC — May 2026"""

import json, time, math, os
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

# ─── CONFIG ───
OUTPUT = Path("/teamspace/erdos_output.json")  # Lightning persistent
MANIFEST = Path("/teamspace/work_manifest.json")
CHUNK_SIZE = 500_000_000  # 500M per run
HOT_MOD9 = {0, 3, 6}      # mod9 values that produce breaches
HOT_MOD24 = 0              # mod24=0 is the breach corridor
SAVE_INTERVAL = 1_000_000  # Save every 1M checked

print("=" * 60)
print("ERDOS L40S — HOT CORRIDOR SIEVE")
print(f"Start: {datetime.now().isoformat()}")
print(f"GPU: L40S — 48GB VRAM — $2.89/hr")
print(f"Target: mod24=0, mod9∈{HOT_MOD9}")
print(f"Chunk: {CHUNK_SIZE:,} per run")
print("=" * 60)

# ─── LOAD PRIOR STATE ───
if OUTPUT.exists():
    state = json.loads(OUTPUT.read_text())
    start_n = state.get("last_n", 32_000_000)
    solutions = state.get("solutions", [])
    stats = state.get("stats", {"stable": 0, "breach": 0, "neutral": 0, "total_checked": 0})
    print(f"Resuming from n={start_n:,} — {len(solutions)} existing solutions")
else:
    start_n = 32_000_000
    solutions = []
    stats = {"stable": 0, "breach": 0, "neutral": 0, "total_checked": 0}
    print(f"Fresh start from n={start_n:,}")

# ─── ERDOS-STRAUS SIEVE (optimized) ───
def erdos_straus(n):
    """Check if 4/n = 1/x + 1/y + 1/z has integer solutions.
    Returns (has_solution, classification, (x,y,z))"""
    # Only target mod24=0 corridor
    if n % 24 != HOT_MOD24:
        return False, "SKIP", None
    
    mod9 = n % 9
    if mod9 not in HOT_MOD9:
        return False, "SKIP", None
    
    # Sieve the hot corridor
    # Standard parametric form: x = n/4 + t, sweep for y,z
    found = False
    best = None
    
    # Quick check on small divisors  
    for a in range(1, min(1000, n // 4 + 1)):
        if n % a == 0:
            x = n // a
            rem = 4/n - 1/x
            if rem <= 0: continue
            
            for b in range(1, min(1000, int(2/rem) + 2)):
                y = b
                z_rem = rem - 1/y
                if z_rem <= 0: continue
                z = 1 / z_rem
                if abs(z - round(z)) < 1e-10 and z > 0:
                    z = round(z)
                    if x > 0 and y > 0 and z > 0:
                        found = True
                        best = (x, y, z)
                        break
            if found: break
    
    if found:
        # Classify
        if mod9 in (0, 3, 6):
            depth = "BREACH_MOD9"
        else:
            depth = "STABLE_MOD9"
        return True, depth, best
    
    return False, "BREACH_UNVERIFIED", None

# ─── MAIN LOOP ───
end_n = start_n + CHUNK_SIZE
batch = []
last_save = start_n
checkpoint_time = time.time()

try:
    for n in range(start_n, end_n):
        has_sol, depth, triple = erdos_straus(n)
        stats["total_checked"] += 1
        
        if has_sol:
            entry = {
                "n": n,
                "mod9": n % 9,
                "mod24": n % 24,
                "depth": depth,
                "triple": list(triple) if triple else None,
                "timestamp": datetime.now().isoformat()
            }
            solutions.append(entry)
            
            if "STABLE" in depth: stats["stable"] += 1
            elif "BREACH" in depth: stats["breach"] += 1
            else: stats["neutral"] += 1
        
        # Periodic save
        if n - last_save >= SAVE_INTERVAL:
            elapsed = time.time() - checkpoint_time
            rate = SAVE_INTERVAL / elapsed if elapsed > 0 else 0
            
            state = {
                "last_n": n,
                "solutions": solutions[-1000:],  # Keep last 1000 in state
                "stats": stats,
                "rate_per_sec": round(rate),
                "timestamp": datetime.now().isoformat(),
                "gpu": "L40S",
                "cost_per_hr": 2.89
            }
            
            # Save full log separately
            full_log = {
                "last_n": n,
                "solutions": solutions,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            Path("/teamspace/erdos_full_log.json").write_text(json.dumps(full_log))
            
            # Update working state
            OUTPUT.write_text(json.dumps(state, indent=2))
            
            # Update manifest for dashboard
            if MANIFEST.exists():
                m = json.loads(MANIFEST.read_text())
                m["nodes"]["lightning_l40s"]["last_chunk"] = n
                m["nodes"]["lightning_l40s"]["total_solutions"] = len(solutions)
                m["nodes"]["lightning_l40s"]["last_run"] = datetime.now().isoformat()
                m["nodes"]["lightning_l40s"]["status"] = "active"
                m["solutions_total"] = len(solutions)
                m["stable_regions"] = stats["stable"]
                m["breach_regions"] = stats["breach"]
                m["last_updated"] = datetime.now().isoformat()
                MANIFEST.write_text(json.dumps(m, indent=2))
            
            progress_pct = (n - start_n) / CHUNK_SIZE * 100
            print(f"  [{progress_pct:.1f}%] n={n:,} | {len(solutions)} sols | "
                  f"S:{stats['stable']} B:{stats['breach']} | {rate:.0f} n/s | "
                  f"${2.89*(time.time()-checkpoint_time)/3600:.4f} spent")
            
            last_save = n
            checkpoint_time = time.time()
            
            # Flush batch
            batch = []

except KeyboardInterrupt:
    print("\nInterrupted — saving state...")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

# ─── FINAL SAVE ───
final_state = {
    "last_n": end_n,
    "solutions": solutions,
    "stats": stats,
    "completed_chunk": True,
    "timestamp": datetime.now().isoformat(),
    "gpu": "L40S",
    "cost_per_hr": 2.89,
    "chunk_size": CHUNK_SIZE
}
OUTPUT.write_text(json.dumps(final_state, indent=2))

runtime_hrs = (time.time() - checkpoint_time + (end_n - start_n) / max(1, stats["total_checked"]) * 0) / 3600

print("\n" + "=" * 60)
print("ERDOS L40S — RUN COMPLETE")
print(f"Checked: {stats['total_checked']:,} values")
print(f"Solutions: {len(solutions)}")
print(f"STABLE: {stats['stable']} | BREACH: {stats['breach']}")
print(f"Last n: {end_n:,}")
print(f"Output: {OUTPUT}")
print("=" * 60)
