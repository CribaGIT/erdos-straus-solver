#!/usr/bin/env python
"""
ERDOS–STRAUS MASTER ORCHESTRATOR — Maximum Automation
Coordinates all 5 compute nodes. Auto-launches what it can.
Replaces individual cron jobs with one unified controller.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, os, sys, time, subprocess
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "Projects/erdos-straus"
MANIFEST_PATH = BASE / "work_manifest.json"
OUTPUT_PATH = BASE / "KAGGLE_OUTPUT_RECORD.jsonl"

# ═══════════════════════════════════════════════════════
# NODE CONTROLLERS
# ═══════════════════════════════════════════════════════

def run_local_victus():
    """Run CLASSIFICATION on existing solutions (fast, seconds).
    The full GPU sieve runs on Kaggle T4. Here we just classify
    the 361 existing solutions into STABLE/BREACH."""
    print("[local_victus] Classifying 361 solutions via mod9 corridor...")
    
    try:
        # Load existing solutions from the output record
        solutions = []
        output_path = BASE / "KAGGLE_OUTPUT_RECORD.jsonl"
        if output_path.exists():
            with open(output_path) as f:
                for line in f:
                    solutions.append(json.loads(line))
        
        if not solutions:
            print("  ⚠ No solutions to classify")
            return None
        
        # Mod9 corridor classification
        stable, breach, unknown = 0, 0, 0
        for sol in solutions:
            # Extract n from vector[0] (the primary integer)
            vector = sol.get('vector', [])
            n = vector[0] if vector else 0
            mod9 = n % 9
            # CLASSIFY: mod9=1,4,7 → STABLE (Erdos corridor)
            #          mod9=0,3,6 → BREACH (potential counterexample regions)
            #          mod9=2,5,8 → unknown (neutral)
            if mod9 in (1, 4, 7):
                stable += 1
            elif mod9 in (0, 3, 6):
                breach += 1
            else:
                unknown += 1
        
        result = {
            "solutions": len(solutions),
            "stable": stable,
            "breach": breach,
            "unknown": unknown,
            "stable_pct": round(stable / max(1, len(solutions)) * 100, 1),
            "breach_pct": round(breach / max(1, len(solutions)) * 100, 1),
            "ts": datetime.now().isoformat()
        }
        
        print(f"  ✓ Classified {len(solutions)} solutions:")
        print(f"    STABLE: {stable} ({result['stable_pct']}%)")
        print(f"    BREACH: {breach} ({result['breach_pct']}%)")
        print(f"    Unknown: {unknown}")
        
        return result
    except Exception as e:
        print(f"  ✗ Classification failed: {e}")
        return None

def try_kaggle_push():
    """Attempt Kaggle kernel push via CLI (may fail)."""
    print("[kaggle_t4] Attempting kernel push...")
    try:
        result = subprocess.run(
            ["kaggle", "kernels", "push"],
            capture_output=True, text=True, timeout=30,
            cwd=str(BASE)
        )
        if result.returncode == 0:
            print("  ✓ Kernel pushed to Kaggle")
            return True
        else:
            print(f"  ✗ Push failed: {result.stderr[:100]}")
            return False
    except:
        print("  ✗ Kaggle CLI not available")
        return False

def try_lightning_launch():
    """Attempt Lightning AI studio launch via SDK."""
    print("[lightning_l40s] Attempting auto-launch...")
    try:
        # Check if Lightning SDK can create studios
        from lightning_sdk import Studio, Machine
        
        studio = Studio(
            name="erdos-sieve-worker",
            teamspace="controlled-copper-5tcd",
            machine=Machine.L40S,
            create_ok=True
        )
        
        # Upload the sieve script
        script = BASE / "lightning_sieve.py"
        if script.exists():
            studio.upload_file(str(script), script.name)
            print(f"  ✓ Uploaded {script.name}")
        
        # Run and detach
        studio.run_and_detach(f"python {script.name} && shutdown")
        print(f"  ✓ Studio launched on L40S — auto-shutdown on completion")
        return True
    except ImportError:
        print("  ✗ Lightning SDK not available")
        return False
    except Exception as e:
        print(f"  ✗ Launch failed: {str(e)[:100]}")
        return False

def check_huggingface_status():
    """Check if HF Space is deployed."""
    print("[huggingface_t4] Checking status...")
    try:
        import urllib.request
        req = urllib.request.Request("https://huggingface.co/api/spaces/commencethescourge/erdos-sieve")
        urllib.request.urlopen(req, timeout=5)
        print("  ✓ Space exists")
        return True
    except:
        print("  ✗ No space deployed — needs Gradio app")
        return False

# ═══════════════════════════════════════════════════════
# MANIFEST MANAGER
# ═══════════════════════════════════════════════════════

def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    # Create fresh
    return {
        "version": "v113",
        "axiom": "STATUTORY_SIEVE_v3",
        "created": datetime.now().isoformat(),
        "total_range": 1_000_000_000_000,
        "current_progress": 100_000_000_000,
        "solutions_total": 0,
        "stable_regions": 0,
        "breach_regions": 0,
        "nodes": {},
        "last_orchestration": None
    }

def save_manifest(m):
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(m, f, indent=2)

def merge_node_result(manifest, node_name, result_data):
    """Merge a node's result into the manifest — idempotent (safe to re-run)."""
    if node_name not in manifest["nodes"]:
        manifest["nodes"][node_name] = {}
    
    node = manifest["nodes"][node_name]
    node["status"] = "active"
    node["last_chunk"] = result_data.get("target", 0)
    node["last_solutions"] = result_data.get("solutions", 0)
    node["last_stable"] = result_data.get("stable", 0)
    node["last_breach"] = result_data.get("breach", 0)
    node["last_run"] = result_data.get("ts", datetime.now().isoformat())
    
    # Use node's own count, not accumulated
    manifest["solutions_total"] = result_data.get("solutions", manifest.get("solutions_total", 0))
    manifest["stable_regions"] = result_data.get("stable", manifest.get("stable_regions", 0))
    manifest["breach_regions"] = result_data.get("breach", manifest.get("breach_regions", 0))
    manifest["current_progress"] = result_data.get("solutions", manifest.get("current_progress", 0))

# ═══════════════════════════════════════════════════════
# MAIN ORCHESTRATOR — called by cron every 6h
# ═══════════════════════════════════════════════════════

def orchestrate():
    print("╔══════════════════════════════════════════════╗")
    print("║  ERDOS–STRAUS MASTER ORCHESTRATOR           ║")
    print(f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                       ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    
    manifest = load_manifest()
    results = {}
    
    # 1. LOCAL — always runs (100% automated)
    print("═══ PHASE 1: LOCAL COMPUTE ═══")
    local_output = run_local_victus()
    if local_output:
        results["local_victus"] = "ran"
        merge_node_result(manifest, "local_victus", {
            "solutions": local_output["solutions"],
            "stable": local_output["stable"],
            "breach": local_output["breach"],
            "target": local_output["solutions"],
            "ts": local_output["ts"]
        })
    else:
        results["local_victus"] = "skipped"
    
    # 2. KAGGLE — try push (may fail)
    print("\n═══ PHASE 2: KAGGLE SYNC ═══")
    kaggle_ok = try_kaggle_push()
    results["kaggle_t4"] = "pushed" if kaggle_ok else "skipped (CLI broken)"
    
    # 3. LIGHTNING — try auto-launch
    print("\n═══ PHASE 3: LIGHTNING LAUNCH ═══")
    lightning_ok = try_lightning_launch()
    results["lightning_l40s"] = "launched" if lightning_ok else "skipped"
    
    # 4. HUGGINGFACE — check status
    print("\n═══ PHASE 4: HUGGINGFACE CHECK ═══")
    hf_ok = check_huggingface_status()
    results["huggingface_t4"] = "deployed" if hf_ok else "not deployed"
    
    # 5. UPDATE MANIFEST
    manifest["last_orchestration"] = datetime.now().isoformat()
    save_manifest(manifest)
    
    # 5b. SAVE CLASSIFICATION LOG
    log_path = BASE / f"daily_logs/classify_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.parent.mkdir(exist_ok=True)
    with open(log_path, 'w') as f:
        json.dump({
            "ts": datetime.now().isoformat(),
            "solutions": manifest["solutions_total"],
            "stable": manifest["stable_regions"],
            "breach": manifest["breach_regions"],
            "nodes": {k: v.get("status","?") for k,v in manifest["nodes"].items()}
        }, f, indent=2)
    print(f"  ✓ Log saved: {log_path.name}")
    
    # 6. REGENERATE DASHBOARD (read-only, don't overwrite manifest)
    print("\n═══ PHASE 5: DASHBOARD ═══")
    total = manifest["solutions_total"]
    stable = manifest["stable_regions"]
    breach = manifest["breach_regions"]
    print(f"  ✓ Dashboard: {total} solutions | STABLE:{stable} BREACH:{breach}")
    
    # 7. GIT AUTO-COMMIT
    try:
        subprocess.run(["git", "add", "work_manifest.json", "daily_logs/"], 
                      cwd=str(BASE), capture_output=True, timeout=10)
        subprocess.run(["git", "commit", "-m", 
                       f"auto: {manifest['solutions_total']} sols, S:{manifest['stable_regions']} B:{manifest['breach_regions']}"],
                      cwd=str(BASE), capture_output=True, timeout=10)
        subprocess.run(["git", "push"], cwd=str(BASE), capture_output=True, timeout=15)
        print("  ✓ Git auto-committed")
    except:
        print("  ⚠ Git push skipped")
    
    # Summary
    print(f"\n═══ ORCHESTRATION COMPLETE ═══")
    for node, status in results.items():
        print(f"  {node:>20}: {status}")

if __name__ == "__main__":
    orchestrate()
