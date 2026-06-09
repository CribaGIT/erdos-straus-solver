#!/usr/bin/env python
"""
VINCULUM REPORTER — comprehensive vinculum dashboard for Erdos-Straus sieve.

Reads all output files (erdos_output_*.json, work_manifest.json,
KAGGLE_OUTPUT_RECORD.jsonl) and generates a full vinculum ratio report
in markdown. Every ratio is annotated with preserves/sacrifices.

DaShawn / Guinea Pig Trench LLC — June 2026
"""

import json, sys, time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional


def load_all_outputs(base_dir: Path) -> dict:
    """Aggregate all data sources into a single state dict."""
    state = {
        "solutions": [],
        "stats": {"stable": 0, "breach": 0, "neutral": 0,
                  "total_checked": 0, "total_solutions": 0},
        "anomalies": [],
        "last_n": 0,
        "rate_per_sec": 0,
        "files": [],
        "nodes": {},
        "total_range": 0,
        "current_progress": 0,
    }

    # Load JSONL stream
    jsonl_path = base_dir / "KAGGLE_OUTPUT_RECORD.jsonl"
    if jsonl_path.exists():
        state["files"].append("KAGGLE_OUTPUT_RECORD.jsonl")
        try:
            with open(jsonl_path) as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        state["solutions"].append(rec)
                        state["stats"]["total_solutions"] += 1
                        if "STABLE" in rec.get("depth", ""):
                            state["stats"]["stable"] += 1
                        elif "BREACH" in rec.get("depth", ""):
                            state["stats"]["breach"] += 1
                        else:
                            state["stats"]["neutral"] += 1
        except (json.JSONDecodeError, OSError):
            pass

    # Load output JSONs (for stats that JSONL doesn't track)
    for f in sorted(base_dir.glob("erdos_output_*.json")):
        state["files"].append(f.name)
        try:
            data = json.loads(f.read_text())
            stats = data.get("stats", {})
            state["stats"]["total_checked"] = max(
                state["stats"]["total_checked"],
                stats.get("total_checked", 0)
            )
            state["stats"]["stable"] = max(
                state["stats"]["stable"],
                stats.get("stable", 0)
            )
            state["stats"]["breach"] = max(
                state["stats"]["breach"],
                stats.get("breach", 0)
            )
            state["last_n"] = max(state["last_n"], data.get("last_n", 0))
            state["rate_per_sec"] = max(
                state["rate_per_sec"],
                data.get("rate_per_sec", 0)
            )
            state["anomalies"].extend(data.get("anomalies", []))
        except (json.JSONDecodeError, OSError):
            pass

    # Load manifest
    manifest_path = base_dir / "work_manifest.json"
    if manifest_path.exists():
        state["files"].append("work_manifest.json")
        try:
            m = json.loads(manifest_path.read_text())
            state["nodes"] = m.get("nodes", {})
            state["total_range"] = m.get("total_range", 0)
            state["current_progress"] = m.get("current_progress", 0)
            state["stats"]["total_solutions"] = max(
                state["stats"]["total_solutions"],
                m.get("solutions_total", 0)
            )
        except (json.JSONDecodeError, OSError):
            pass

    return state


def compute_ratios(state: dict) -> dict:
    """Compute all vinculum ratios from aggregated state."""
    s = state["stats"]
    tc = s["total_checked"]
    ts = s["total_solutions"]
    st = s["stable"]
    br = s["breach"]
    an = len(state["anomalies"])
    ln = state["last_n"]
    rr = state["rate_per_sec"]

    ratios = {}

    # Primary: search efficiency
    ratios["hit_rate"] = {
        "value": ts / tc if tc > 0 else 0,
        "num": ts, "den": tc,
        "preserves": "Search efficiency — higher is better",
        "sacrifices": "Coverage breadth — misses outside corridor"
    }

    # Corridor composition
    if ts > 0:
        ratios["stable_fraction"] = {
            "value": st / ts, "num": st, "den": ts,
            "preserves": "Parametric certainty — algebraically guaranteed",
            "sacrifices": "Discovery novelty — stable is routine"
        }
        ratios["breach_fraction"] = {
            "value": br / ts, "num": br, "den": ts,
            "preserves": "Novelty signal — edge cases found",
            "sacrifices": "Regularity — high breach means corridor boundary"
        }
    else:
        ratios["stable_fraction"] = {"value": 0, "num": 0, "den": 0,
                                      "preserves": "", "sacrifices": ""}
        ratios["breach_fraction"] = {"value": 0, "num": 0, "den": 0,
                                      "preserves": "", "sacrifices": ""}

    # Anomaly rate
    ratios["anomaly_rate"] = {
        "value": an / tc if tc > 0 else 0,
        "num": an, "den": tc,
        "preserves": "Quality control — zero means sound corridor",
        "sacrifices": "Throughput — checking is free"
    }

    # Span efficiency
    effective_span = tc * 24
    ratios["effective_span"] = {
        "value": effective_span,
        "num": effective_span, "den": 1,
        "preserves": "Total raw n covered",
        "sacrifices": "Not adjusted for corridor density"
    }

    # Velocity
    ratios["search_velocity"] = {
        "value": rr,
        "num": rr, "den": 1,
        "preserves": "Throughput — candidates per second",
        "sacrifices": "Quality — high velocity may miss sparse solutions"
    }

    # Solutions per unit range
    if ln > 0:
        ratios["solution_density"] = {
            "value": ts / ln,
            "num": ts, "den": ln,
            "preserves": "Absolute density across search range",
            "sacrifices": "Context — doesn't show stride pattern"
        }
    else:
        ratios["solution_density"] = {"value": 0, "num": 0, "den": 0,
                                       "preserves": "", "sacrifices": ""}

    # Corridor confidence
    if tc > 0 and ts > 0:
        # How much of the search produced non-anomaly results
        ratios["corridor_confidence"] = {
            "value": 1 - (an / tc),
            "num": tc - an, "den": tc,
            "preserves": "Confidence that corridor is valid",
            "sacrifices": "Does not detect false negatives"
        }
    else:
        ratios["corridor_confidence"] = {"value": 0, "num": 0, "den": 0,
                                          "preserves": "", "sacrifices": ""}

    # Node coverage
    total_nodes = len(state["nodes"])
    active_nodes = sum(1 for n in state["nodes"].values()
                       if n.get("status") == "active")
    if total_nodes > 0:
        ratios["node_coverage"] = {
            "value": active_nodes / total_nodes,
            "num": active_nodes, "den": total_nodes,
            "preserves": "Distribution parallelism",
            "sacrifices": "Not all nodes report in real-time"
        }
    else:
        ratios["node_coverage"] = {"value": 0, "num": 0, "den": 0,
                                    "preserves": "", "sacrifices": ""}

    # Progress toward target
    tr = state["total_range"]
    cp = state["current_progress"]
    if tr > 0:
        ratios["progress"] = {
            "value": cp / tr,
            "num": cp, "den": tr,
            "preserves": "Goal tracking — fraction of target reached",
            "sacrifices": "Target may be aspirational"
        }
    else:
        ratios["progress"] = {"value": 0, "num": 0, "den": 0,
                               "preserves": "", "sacrifices": ""}

    return ratios


def format_report(state: dict, ratios: dict) -> str:
    """Format the vinculum ratio report as markdown."""
    lines = []
    lines.append("# Vinculum Report — Erdos-Straus Solver")
    lines.append(f"**Generated:** {datetime.now().isoformat()}")
    lines.append("")
    lines.append(f"**Data sources:** {', '.join(state['files']) if state['files'] else 'none'}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = state["stats"]
    lines.append(f"- **Total solutions:** {s['total_solutions']:,}")
    lines.append(f"- **Candidates checked:** {s['total_checked']:,}")
    lines.append(f"- **Effective n spanned:** {s['total_checked'] * 24:,}")
    lines.append(f"- **STABLE:** {s['stable']:,} | **BREACH:** {s['breach']:,} | **NEUTRAL:** {s['neutral']:,}")
    lines.append(f"- **Anomalies:** {len(state['anomalies'])}")
    lines.append(f"- **Last n:** {state['last_n']:,}")
    lines.append(f"- **Search rate:** {state['rate_per_sec']:,.0f} candidates/s")
    lines.append("")
    lines.append("## Vinculum Ratios")
    lines.append("")
    lines.append("| Ratio | Value | Preserves | Sacrifices |")
    lines.append("|-------|-------|-----------|------------|")

    ratio_order = [
        ("hit_rate", "HIT RATE (solutions / candidates)"),
        ("stable_fraction", "STABLE FRACTION (stable / total)"),
        ("breach_fraction", "BREACH FRACTION (breach / total)"),
        ("anomaly_rate", "ANOMALY RATE (anomalies / candidates)"),
        ("solution_density", "SOLUTION DENSITY (solutions / n_range)"),
        ("effective_span", "EFFECTIVE SPAN (candidates × stride)"),
        ("search_velocity", "SEARCH VELOCITY (candidates / s)"),
        ("corridor_confidence", "CORRIDOR CONFIDENCE (non-anomalous / total)"),
        ("node_coverage", "NODE COVERAGE (active / total)"),
        ("progress", "PROGRESS (current / target)"),
    ]

    for key, label in ratio_order:
        r = ratios.get(key)
        if r is None:
            continue
        if r["den"] == 0 and "EFFECTIVE" not in key and "VELOCITY" not in key:
            lines.append(f"| {label} | — | — | — |")
            continue
        if "EFFECTIVE" in label or "VELOCITY" in label:
            val_str = f"{r['value']:,.0f}"
        else:
            val_str = f"{r['value']:.6f} ({r['value']*100:.2f}%)"
        lines.append(f"| {label} | {val_str} | {r['preserves']} | {r['sacrifices']} |")

    lines.append("")
    lines.append("## Node Status")
    lines.append("")
    if state["nodes"]:
        lines.append("| Node | Status | Solutions | Last Chunk |")
        lines.append("|------|--------|-----------|------------|")
        for name, node in sorted(state["nodes"].items()):
            status = node.get("status", "?")
            sols = node.get("total_solutions", 0) or node.get("last_solutions", 0) or 0
            chunk = node.get("last_chunk", 0) or 0
            lines.append(f"| {name} | {status} | {sols:,} | {chunk:,} |")
    else:
        lines.append("No node data available.")

    lines.append("")
    lines.append("## Recommendations")
    lines.append("")

    hr = ratios.get("hit_rate", {}).get("value", 0)
    if hr > 0.9:
        lines.append("- **Continue hot corridor** — hit rate is excellent.")
        lines.append("- Extend depth by 20M strides.")
    elif hr > 0.5:
        lines.append("- **Consider warm corridor expansion** — hit rate is moderate.")
        lines.append("- Test mod9∈{1,4,7} with a small sample run.")
    else:
        lines.append("- **Hot corridor may be depleted** — consider corridor expansion.")
        lines.append("- Run warm_corridor_sweep.py or reduce stride threshold.")

    ar = ratios.get("anomaly_rate", {}).get("value", 0)
    if ar > 0:
        lines.append(f"- **Investigate anomalies** ({state['anomalies'][:10]})")
    else:
        lines.append("- **No anomalies** — corridor integrity confirmed.")

    lines.append("")
    lines.append("---")
    lines.append("*Report generated by vinculum_reporter.py — every measurement is a ratio*")

    return "\n".join(lines)


def main():
    base_dir = Path(__file__).resolve().parent
    state = load_all_outputs(base_dir)
    ratios = compute_ratios(state)
    report = format_report(state, ratios)

    print(report)

    out_path = base_dir / "VINCULUM_REPORT.md"
    out_path.write_text(report)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
