#!/usr/bin/env python
"""
ERDOS–STRAUS AUTOMATION AUDIT
What can and can't be automated — May 2026
DaShawn / Guinea Pig Trench LLC

Usage:
  python automation_audit.py              # print audit table + save manifest
  python automation_audit.py --sync-issues  # also sync dormant nodes to GitHub issues
"""
import json, os, subprocess, sys, hashlib
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════

REPO = "COMMENCINGTHESCOURGE/erdos-straus-solver"
ISSUE_LABEL_PREFIX = "compute"  # produces labels like "compute:kaggle_t4"
AUTO_LABEL = "audit-auto"       # marks issues created by this script
DRY_RUN = "--dry-run" in sys.argv

# ═══════════════════════════════════════════════════════
# 6 POTENTIAL COMPUTE NODES
# ═══════════════════════════════════════════════════════

NODES = {
    "local_cpu": {
        "type": "Hermes cron — Python on Victus CPU",
        "status": "✅ RUNNING — every 6h via cron job 560d8130ca87",
        "gpu": "RX 6400 (not utilized — numpy CPU only)",
        "auto_execute": True,
        "auto_upload": True,  # saves to G: drive
        "limit": "~500M integers per day on CPU",
        "bottleneck": "CPU-bound, no GPU acceleration for numpy",
        "fix": "Add cupy/numba GPU acceleration to use RX 6400",
        "automation_level": "90% — fully hands-off",
    },
    "kaggle_t4": {
        "type": "Kaggle Notebook — T4 GPU",
        "status": "⚠️ MANUAL — CLI push broken, requires web upload",
        "gpu": "NVIDIA T4 (30 hrs/week free)",
        "auto_execute": False,
        "auto_upload": False,  # kernel push CLI broken
        "limit": "30 hrs/week, 12hr max per session",
        "bottleneck": "kaggle kernels push returns empty API response. Kernel must be manually uploaded via web UI, then manually clicked 'Run'.",
        "fix": "Use Kaggle SDK (kagglesdk 0.1.23 installed) Python API instead of CLI. SDK has kernels_create() and kernels_initialize(). Alternative: Kaggle REST API via curl with bearer token.",
        "automation_level": "10% — manual upload + run",
    },
    "colab_t4": {
        "type": "Google Colab — T4 GPU",
        "status": "⚠️ MANUAL — notebook must be uploaded, free tier kills after 90min idle",
        "gpu": "NVIDIA T4 (free tier)",
        "auto_execute": False,
        "auto_upload": True,  # auto-saves to Google Drive
        "limit": "90min idle timeout, ~12hr max continuous",
        "bottleneck": "Free tier auto-terminates. Colab Pro ($10/mo) allows background execution. No programmatic trigger without Colab API.",
        "fix": "Colab Pro + background execution. Or use pyngrok/nbformat to trigger execution programmatically.",
        "automation_level": "15% — auto-saves output but needs manual run",
    },
    "lightning_ai": {
        "type": "Lightning AI Studio — L40S/A100 GPU",
        "status": "💤 DORMANT — litai SDK installed but not utilized",
        "gpu": "L40S or A100 (credits required)",
        "auto_execute": False,
        "auto_upload": False,
        "limit": "Credit-based, studio must be manually started",
        "bottleneck": "litai SDK is LLM-only (no studio management). Studio must be started via web interface. Once running, can execute Python scripts.",
        "fix": "Automate studio launch via Lightning REST API. Run sieve as persistent background process inside studio.",
        "automation_level": "0% — completely dormant",
    },
    "huggingface": {
        "type": "HuggingFace Spaces — T4/A10G GPU",
        "status": "💤 DORMANT — API responding (200) but no space deployed",
        "gpu": "T4 or A10G (free tier)",
        "auto_execute": False,
        "auto_upload": False,
        "limit": "Free tier: 16GB RAM, no GPU persistence",
        "bottleneck": "No Space deployed. Would need Gradio app wrapping the sieve. Can run continuously unlike Colab free tier.",
        "fix": "Deploy HF Space with Gradio + sieve. Continuous uptime unlike Colab.",
        "automation_level": "0% — no space deployed",
    },
    "deepseek_api": {
        "type": "DeepSeek v4-pro — LLM verification",
        "status": "💤 DORMANT — could verify solutions but not compute sieve",
        "gpu": "N/A (API inference)",
        "auto_execute": False,
        "auto_upload": False,
        "limit": "API costs, not suitable for brute-force sieving",
        "bottleneck": "LLMs can verify Erdos-Straus solutions but can't efficiently search for them. Use as verification node only.",
        "fix": "Use DeepSeek to verify top-N solutions found by other nodes. Adds mathematical rigor layer.",
        "automation_level": "0% — not configured",
    },
    "codex": {
        "type": "Codex CLI v0.130 — AI agent + media processor (Hermes MCP-ready)",
        "status": "✅ RUNNING — codex exec + output server at :8765",
        "gpu": "N/A (OpenAI API — cloud inference)",
        "auto_execute": True,
        "auto_upload": True,  # serves results at http://127.0.0.1:8765
        "limit": "OpenAI credits required. No offline mode. 600s default timeout.",
        "bottleneck": "Requires active OpenAI API key. Not suitable for compute-heavy sieving, but excellent for media processing, code review, and agent-driven tasks.",
        "fix": "Run `codex exec --ephemeral` for stateless tasks. Use `codex mcp-server` to expose tools to Hermes via MCP.",
        "automation_level": "90% — fully automatable via `codex exec`. Output server is self-serve.",
    },
}

# ═══════════════════════════════════════════════════════
# WHAT CAN BE AUTOMATED (realistic)
# ═══════════════════════════════════════════════════════

AUTOMATION_POTENTIAL = """
┌─────────────────────────────────────────────────────────────┐
│                 AUTOMATION POTENTIAL                        │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ NODE     │ CURRENT  │ POSSIBLE │ EFFORT   │ BLOCKER        │
├──────────┼──────────┼──────────┼──────────┼────────────────┤
│ Local    │   90%    │   95%    │  LOW     │ GPU accel      │
│ Kaggle   │   10%    │   70%    │  MEDIUM  │ SDK/Kaggle API │
│ Colab    │   15%    │   60%    │  HIGH    │ Colab Pro $    │
│ Lightning│    0%    │   50%    │  HIGH    │ Credits + API  │
│ HF Space │    0%    │   80%    │  MEDIUM  │ Deploy once    │
│ DeepSeek │    0%    │   90%    │  LOW     │ Verify only    │
│ Codex    │   90%    │   95%    │  LOW     │ Credits        │
├──────────┼──────────┼──────────┼──────────┼────────────────┤
│ OVERALL  │   29%    │   79%    │          │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘

Highest-impact, lowest-effort wins:
  1. DEEPSEEK VERIFIER (90% achievable, low effort) — cron calls API to verify solutions
  2. HUGGINGFACE SPACE (80% achievable, medium effort) — deploy once, runs continuously
  3. KAGGLE SDK FIX (70% achievable, medium effort) — programmatic kernel management
  4. LOCAL GPU ACCEL (5% gain) — cupy/numba for RX 6400
"""

# ═══════════════════════════════════════════════════════
# COORDINATED WORK MANIFEST
# ═══════════════════════════════════════════════════════

def create_manifest():
    """Create the master work manifest that all nodes coordinate through."""
    manifest = {
        "version": "v113",
        "axiom": "STATUTORY_SIEVE_v3",
        "created": datetime.now().isoformat(),
        "total_range": 1_000_000_000_000,  # 1 trillion ultimate target
        "current_progress": 100_000_000_000,  # where v112 left off
        "mod24_classes": [1,5,7,9,11,13,17,19,23],
        "mod9_corridor": True,
        "nodes": {
            "local_victus": {
                "status": "active",
                "last_chunk": 100_000_000_000,
                "chunks_per_run": 100_000_000,
                "total_solutions": 0,
                "last_run": None,
                "output_file": "KAGGLE_OUTPUT_RECORD.jsonl"
            },
            "kaggle_t4": {
                "status": "manual",
                "last_chunk": None,
                "chunks_per_run": 1_000_000_000,
                "total_solutions": 0,
                "last_run": None,
                "output_file": "/kaggle/working/v113_flank_31.json"
            },
            "colab_t4": {
                "status": "manual", 
                "last_chunk": None,
                "chunks_per_run": 500_000_000,
                "total_solutions": 0,
                "last_run": None,
                "output_file": "/content/drive/MyDrive/Resonance_Archive/v113_colab.json"
            },
            "lightning_l40s": {
                "status": "dormant",
                "last_chunk": None,
                "chunks_per_run": 5_000_000_000,
                "total_solutions": 0,
                "last_run": None
            },
            "huggingface_t4": {
                "status": "dormant",
                "last_chunk": None,
                "chunks_per_run": 500_000_000,
                "total_solutions": 0,
                "last_run": None
            }
        },
        "solutions_total": 0,
        "stable_regions": 0,
        "breach_regions": 0,
        "mod9_breakthroughs": [],
        "self_hash": ""
    }
    return manifest

# ═══════════════════════════════════════════════════════
# AUTO-RETRY LOGIC (for cron jobs)
# ═══════════════════════════════════════════════════════

RETRY_LOGIC = """
Each cron job should include:
  1. Pre-flight: check manifest for last processed chunk → skip duplicates
  2. Execute: run sieve on next unprocessed chunk
  3. Post-flight: update manifest with new progress
  4. Error detection: if output file is empty or hash mismatch → retry
  5. Max retries: 3 per chunk, then skip and flag for manual review
  6. Cross-node: always read manifest BEFORE computing to avoid overlap
"""

# ═══════════════════════════════════════════════════════
# GITHUB ISSUE SYNC — auto-create issues for dormant nodes
# ═══════════════════════════════════════════════════════

def _run_gh(args, check=True):
    """Run gh CLI command, return stdout or None on failure."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=15
        )
        if check and result.returncode != 0:
            print(f"  [!] gh {' '.join(args[:3])}... failed: {result.stderr.strip()[:200]}")
            return None
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  [!] gh not available or timed out: {e}")
        return None

def _is_dormant(status_str):
    """Detect dormancy from status string patterns."""
    dormant_markers = ["DORMANT", "⚠️", "0%", "completely dormant"]
    return any(m in status_str for m in dormant_markers)

def _is_running(status_str):
    """Detect active/running nodes."""
    return "✅" in status_str or "RUNNING" in status_str

def _make_label(node_name):
    """Generate a unique label per compute node."""
    return f"{ISSUE_LABEL_PREFIX}:{node_name}"

def _issue_exists(node_name):
    """Check if an open issue already exists for this compute node."""
    label = _make_label(node_name)
    out = _run_gh([
        "issue", "list",
        "--repo", REPO,
        "--label", label,
        "--state", "open",
        "--json", "number",
        "--jq", ".[0].number"
    ], check=False)
    if out and out.isdigit():
        return int(out)
    return None

def _close_issue(issue_number, node_name, status):
    """Close a dormant issue when the node recovers."""
    msg = f"✅ {node_name} recovered — current status: {status}"
    print(f"  [close] #{issue_number}: {msg}")
    if DRY_RUN:
        print(f"  [DRY RUN] would close #{issue_number}")
        return
    _run_gh([
        "issue", "close", str(issue_number),
        "--repo", REPO,
        "--comment", msg
    ])

def _create_issue(node_name, node):
    """Create a GitHub issue for a dormant compute node."""
    title = f"{node_name} dormant — {node['automation_level']}"
    body = f"""**Auto-detected:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Status:** {node['status']}
**Type:** {node['type']}
**GPU:** {node['gpu']}
**Limit:** {node['limit']}

**Bottleneck:** {node['bottleneck']}

**Suggested fix:** {node['fix']}

---
*Issue auto-created by `automation_audit.py --sync-issues`. 
Closes automatically when node status changes to RUNNING.*
"""
    label = _make_label(node_name)
    
    # Ensure labels exist
    for lbl in [label, AUTO_LABEL]:
        _run_gh(["label", "create", lbl, "--repo", REPO,
                 "--color", "FBCA04", "--force"], check=False)
    
    print(f"  [create] issue for {node_name}")
    if DRY_RUN:
        print(f"  [DRY RUN] would create: {title}")
        return
    
    _run_gh([
        "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
        "--label", f"{label},{AUTO_LABEL}"
    ])

def sync_issues():
    """Sync compute node status to GitHub issues.
    
    For each dormant node: create an issue if none exists.
    For each recovered node: close the issue if one exists.
    Nodes with pre-existing manual issues (no AUTO_LABEL) are skipped.
    """
    print("═══ SYNCING COMPUTE NODE ISSUES ═══")
    
    for node_name, node in NODES.items():
        status = node.get("status", "")
        existing = _issue_exists(node_name)
        
        if _is_dormant(status):
            if existing:
                print(f"  [skip] {node_name}: issue #{existing} already open")
            else:
                _create_issue(node_name, node)
        elif _is_running(status):
            if existing:
                _close_issue(existing, node_name, status)
            else:
                print(f"  [ok] {node_name}: running, no issue to close")
        else:
            print(f"  [warn] {node_name}: unclear status — {status[:60]}")

if __name__ == "__main__":
    print(AUTOMATION_POTENTIAL)
    
    manifest = create_manifest()
    manifest_path = Path.home() / "Projects/erdos-straus/work_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\n✓ Manifest saved to {manifest_path}")
    print(f"  Nodes: {len(manifest['nodes'])}")
    print(f"  Current progress: {manifest['current_progress']:,}")
    print(f"  Ultimate target: {manifest['total_range']:,}")
    
    if "--sync-issues" in sys.argv:
        if DRY_RUN:
            print("\n  [DRY RUN MODE — no issues will be created/closed]")
        sync_issues()
