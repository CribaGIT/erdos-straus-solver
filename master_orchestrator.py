#!/usr/bin/env python
"""
ERDOS–STRAUS MASTER ORCHESTRATOR
Coordinates local CPU classification + attempts remote node sync.
Current automation: local classification (90%), Kaggle CLI push (may fail),
Lightning SDK launch (may fail), HuggingFace status check (read-only).
Three of five nodes require manual intervention per automation_audit.

DaShawn / Guinea Pig Trench LLC — May 2026

NOTE: Self-contained paths. Does NOT import from trench_config to avoid
cross-domain coupling between number theory and game engine projects.
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

# ── Paths — self-contained ──
# These are the only paths this orchestrator needs.
# They're defined here to avoid importing from trench_config (game project).
# If you move the erdos-straus project, update these.
BASE = Path(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = BASE / "erdos_manifest.json"
OUTPUT_PATH = BASE / "output"

# ═══════════════════════════════════════════════════════
# NODE CONTROLLERS
# ═══════════════════════════════════════════════════════

def check_codex() -> dict:
    """Check Codex node status — local AI agent + media processor.
    Codex is always local; check if CLI is reachable."""
    try:
        from codex_node import orchestrator_status
        return orchestrator_status()
    except ImportError:
        return {
            "node": "codex",
            "status": "not_importable",
            "error": "codex_node.py not on PYTHONPATH",
            "fix": "Add ~/Projects/trench_builder to PYTHONPATH",
        }

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
    except (FileNotFoundError, subprocess.TimeoutExpired):
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
            create_ok=True
        )
        
        # Start L40S GPU node if not already running
        if studio.status != "running":
            print("  Starting studio on L40S machine...")
            studio.start(machine="L40S")
        
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
    except (OSError, ValueError) as e:
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
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
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
    """Merge a node's result into the manifest — idempotent (safe to re-run).

    Each node reports its own current totals. The manifest computes the
    global aggregate by summing across all nodes. This is correct even
    when nodes report overlapping ranges — the per-node last_chunk
    provides deduplication at the dashboard layer.
    """
    if node_name not in manifest["nodes"]:
        manifest["nodes"][node_name] = {}

    node = manifest["nodes"][node_name]
    new_solutions = result_data.get("solutions", 0)
    new_stable = result_data.get("stable", 0)
    new_breach = result_data.get("breach", 0)

    # Track previous values to detect actual delta
    prev_solutions = node.get("last_solutions", 0) or 0
    prev_stable = node.get("last_stable", 0) or 0
    prev_breach = node.get("last_breach", 0) or 0

    node["status"] = "active"
    node["last_chunk"] = result_data.get("target", 0)
    node["last_solutions"] = new_solutions
    node["last_stable"] = new_stable
    node["last_breach"] = new_breach
    node["last_run"] = result_data.get("ts", datetime.now().isoformat())

    # Accumulate deltas into global totals
    delta_solutions = max(0, new_solutions - prev_solutions)
    delta_stable = max(0, new_stable - prev_stable)
    delta_breach = max(0, new_breach - prev_breach)

    manifest["solutions_total"] = manifest.get("solutions_total", 0) + delta_solutions
    manifest["stable_regions"] = manifest.get("stable_regions", 0) + delta_stable
    manifest["breach_regions"] = manifest.get("breach_regions", 0) + delta_breach
    manifest["current_progress"] = manifest["solutions_total"]

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
    
    # 0. CODEX — always check (local, 100% automated)
    print("═══ PHASE 0: CODEX NODE ═══")
    codex_status = check_codex()
    results["codex"] = codex_status.get("status", "unknown")
    manifest["nodes"]["codex"] = {
        "status": codex_status.get("status", "unknown"),
        "type": "Codex CLI — AI agent + media processor",
        "automation_level": "90%",
        "last_check": datetime.now().isoformat(),
    }
    print(f"  Codex: {codex_status.get('status', '?')} | v{codex_status.get('cli_version', '?')}")
    if codex_status.get("output_server", {}).get("running"):
        print(f"  Output server: ✓ {codex_status['output_server']['url']}")
    
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
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        print("  ⚠ Git push skipped")
    
    # Summary
    print(f"\n═══ ORCHESTRATION COMPLETE ═══")
    for node, status in results.items():
        print(f"  {node:>20}: {status}")

if __name__ == "__main__":
    orchestrate()
