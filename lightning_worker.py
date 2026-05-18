#!/usr/bin/env python
"""
ERDOS–STRAUS LIGHTNING AI WORKER — 4th Compute Node
Uses Lightning AI Studio GPU for distributed sieving.
DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, sys, time
from pathlib import Path

# ═══════════════════════════════════════════════════════
# STUDIO CONFIG
# ═══════════════════════════════════════════════════════

STUDIO_CONFIG = {
    "studio_name": "erdos-sieve-worker",
    "machine_type": "L40S",  # or A100_40GB, A100_80GB
    "teamspace": "controlled-copper-5tcd",  # from memory
    "auto_shutdown": 3600,  # shut down after 1hr idle
}

# ═══════════════════════════════════════════════════════
# SIEVE SCRIPT (uploaded to studio)
# ═══════════════════════════════════════════════════════

SIEVE_SCRIPT = '''
import numpy as np, json, time, hashlib, os
from datetime import datetime

# GPU check
try:
    import torch
    GPU = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except:
    GPU = "CPU"
    DEVICE = "cpu"

print(f"Lightning Worker: {GPU} on {DEVICE}")

TARGET = 5_000_000_000  # 5B — larger chunk for L40S
CHUNK = 10_000_000
MOD24 = [1,5,7,9,11,13,17,19,23]

def sieve(start, end, mod24_classes):
    sols = []
    n_vals = np.arange(start, end, dtype=np.int64)
    for mc in mod24_classes:
        cands = n_vals[n_vals % 24 == mc]
        for n in cands[:500]:
            xs = max(1,(n+3)//4); xe=n*2
            step = max(1,(xe-xs)//60)
            for x in range(xs, xe+1, step):
                d=4*x-n
                if d<=0: continue
                ys = max(1,(n*x+d-1)//d)
                ye = 2*n*x//d if d>0 else n*2
                if ye<ys: continue
                for y in range(ys, min(ye+1,ys+40)):
                    dz=4*x*y-n*(x+y)
                    if dz>0 and (n*x*y)%dz==0:
                        z=(n*x*y)//dz
                        if z>0: sols.append({"n":int(n),"x":int(x),"y":int(y),"z":int(z),"m":mc}); break
                if sols: break
    return sols

total, stable, breach = 0,0,0
for cs in range(2, TARGET, CHUNK):
    ce = min(cs+CHUNK, TARGET)
    sols = sieve(cs, ce, MOD24)
    total += len(sols)
    if sols:
        tors = [s["n"]*s["z"]/(s["x"]+s["y"]) for s in sols if s["x"]+s["y"]>0]
        if tors and len(tors)>1:
            if np.std(tors)/(np.mean(tors)+1) < 0.3: stable += 1
            else: breach += 1
    if ce % 500_000_000 == 0:
        print(f"  [{ce/TARGET*100:.1f}%] {total} sols | S:{stable} B:{breach}")

out = {"node":"lightning_l40s","gpu":GPU,"target":TARGET,"solutions":total,"stable":stable,"breach":breach,"ts":datetime.now().isoformat()}
with open("/teamspace/erdos_output.json","w") as f: json.dump(out,f,indent=2)
print(f"DONE: {total:,} solutions | STABLE:{stable} BREACH:{breach}")
'''

# ═══════════════════════════════════════════════════════
# STUDIO LAUNCHER (CLI-based)
# ═══════════════════════════════════════════════════════

def launch_studio():
    """Launch Lightning AI Studio with the sieve script."""
    # Write the script to a temp file
    script_path = Path.home() / "Projects/erdos-straus/lightning_sieve.py"
    script_path.write_text(SIEVE_SCRIPT)
    
    print(f"═══ LIGHTNING AI WORKER ═══")
    print(f"Studio: {STUDIO_CONFIG['studio_name']}")
    print(f"GPU: {STUDIO_CONFIG['machine_type']}")
    print(f"Teamspace: {STUDIO_CONFIG['teamspace']}")
    print(f"Auto-shutdown: {STUDIO_CONFIG['auto_shutdown']}s")
    print()
    print(f"Script: {script_path} ({script_path.stat().st_size} bytes)")
    print()
    print("To launch manually:")
    print(f"  1. Go to https://lightning.ai/studios")
    print(f"  2. Open teamspace: {STUDIO_CONFIG['teamspace']}")
    print(f"  3. New Studio → {STUDIO_CONFIG['machine_type']}")
    print(f"  4. Upload {script_path.name}")
    print(f"  5. Run: python {script_path.name}")
    print()
    print("After completion, output will be at /teamspace/erdos_output.json")
    print("Download and merge with local KAGGLE_OUTPUT_RECORD.jsonl")

def check_status():
    """Check if a Lightning studio is currently running."""
    print("Checking Lightning AI status...")
    print("→ https://lightning.ai/studios")
    print("  Teamspace: controlled-copper-5tcd")
    print("  Look for: erdos-sieve-worker")
    print("  If running: check /teamspace/erdos_output.json")

# ═══════════════════════════════════════════════════════
# MANIFEST INTEGRATION
# ═══════════════════════════════════════════════════════

def update_manifest(output_path=None):
    """Update work_manifest.json with Lightning results."""
    manifest_path = Path.home() / "Projects/erdos-straus/work_manifest.json"
    
    if not manifest_path.exists():
        print("No manifest found")
        return
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    if output_path and Path(output_path).exists():
        with open(output_path) as f:
            result = json.load(f)
        
        node = manifest["nodes"]["lightning_l40s"]
        node["status"] = "active"
        node["last_chunk"] = result.get("target", 0)
        node["total_solutions"] += result.get("solutions", 0)
        node["last_run"] = result.get("ts")
        
        manifest["solutions_total"] += result.get("solutions", 0)
        manifest["stable_regions"] += result.get("stable", 0)
        manifest["breach_regions"] += result.get("breach", 0)
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("✓ Manifest updated with Lightning results")

if __name__ == "__main__":
    if "--status" in sys.argv:
        check_status()
    elif "--merge" in sys.argv and len(sys.argv) > 2:
        update_manifest(sys.argv[2])
    else:
        launch_studio()
