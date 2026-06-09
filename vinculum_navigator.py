#!/usr/bin/env python
"""
VINCULUM NAVIGATOR — vinculum-guided corridor explorer for Erdos-Straus.

Instead of fixed stride-24 sieving, this module reads sieve output,
computes vinculum ratios (hit rate, corridor density, verification rate),
and uses them to navigate the search space:

  If solutions / candidates > threshold → continue current corridor
  If solutions / candidates < threshold → suggest neighboring corridor
  If anomalies / candidates > 0         → flag for investigation

This turns the vinculum from a post-hoc measurement into an ACTIVE
search heuristic — the ratio itself drives the next step.

DaShawn / Guinea Pig Trench LLC — June 2026
"""

import json, sys, os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional

# ─── Vinculum Ratio Types ───

class VinculumRatio:
    """A single vinculum ratio with preserves/sacrifices annotation."""

    def __init__(self, name: str, numerator: float, denominator: float,
                 preserves: str, sacrifices: str):
        self.name = name
        self.numerator = numerator
        self.denominator = denominator
        self.preserves = preserves
        self.sacrifices = sacrifices
        self.value = numerator / denominator if denominator > 0 else 0.0

    def __repr__(self) -> str:
        pct = self.value * 100
        return (f"  {self.name:>40}: {self.numerator:>12,.0f} / {self.denominator:>12,.0f}"
                f" = {self.value:.6f} ({pct:.2f}%)")


# ─── Corridor Navigator ───

class VinculumNavigator:
    """Reads sieve output and navigates the search space using vinculum ratios."""

    CORRIDORS = {
        "hot": {"mod24": [0], "mod9": [0, 3, 6], "label": "Hot corridor (stride-24, mod9∈{0,3,6})"},
        "warm_a": {"mod24": [0], "mod9": [1, 4, 7], "label": "Warm corridor A (mod24=0, mod9∈{1,4,7})"},
        "warm_b": {"mod24": [0], "mod9": [2, 5, 8], "label": "Warm corridor B (mod24=0, mod9∈{2,5,8})"},
        "cold_1": {"mod24": [1], "mod9": [], "label": "Cold corridor (mod24=1)"},
        "cold_2": {"mod24": [2], "mod9": [], "label": "Cold corridor (mod24=2)"},
    }

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent
        self.ratios: list[VinculumRatio] = []
        self.suggestions: list[str] = []

    def load_outputs(self) -> list[dict]:
        """Load all erdos_output_*.json files and work_manifest.json."""
        outputs = []
        for f in sorted(self.base_dir.glob("erdos_output_*.json")):
            try:
                outputs.append(json.loads(f.read_text()))
            except (json.JSONDecodeError, OSError):
                print(f"  ⚠ Skipping unreadable: {f.name}")
        manifest_path = self.base_dir / "work_manifest.json"
        if manifest_path.exists():
            try:
                outputs.append(json.loads(manifest_path.read_text()))
            except (json.JSONDecodeError, OSError):
                pass
        return outputs

    def compute_ratios(self, data: list[dict]) -> list[VinculumRatio]:
        """Compute all vinculum ratios from output data."""
        ratios = []

        total_solutions = sum(d.get("total_solutions", 0) or
                              d.get("stats", {}).get("total_solutions", 0) or
                              d.get("solutions_total", 0) for d in data)
        total_checked = sum(d.get("stats", {}).get("total_checked", 0) for d in data)
        stable = sum(d.get("stats", {}).get("stable", 0) for d in data)
        breach = sum(d.get("stats", {}).get("breach", 0) for d in data)
        anomalies = sum(len(d.get("anomalies", [])) for d in data)

        # 1. hit rate — the primary vinculum
        ratios.append(VinculumRatio(
            "HIT RATE (solutions / candidates)", total_solutions, total_checked,
            "Search efficiency — higher means better corridor targeting",
            "Coverage breadth — misses solutions outside the corridor"
        ))

        # 2. corridor balance — stable vs breach
        if total_solutions > 0:
            ratios.append(VinculumRatio(
                "CORRIDOR BALANCE (stable / total)", stable, total_solutions,
                "Stability signal — STABLE solutions are parametrically guaranteed",
                "Diversity — ignores BREACH solutions which may reveal structure"
            ))
            ratios.append(VinculumRatio(
                "BREACH DENSITY (breach / total)", breach, total_solutions,
                "Novelty signal — BREACH solutions may be edge cases",
                "Regularity — high breach suggests corridor boundary"
            ))

        # 3. anomaly rate
        if total_checked > 0:
            ratios.append(VinculumRatio(
                "ANOMALY RATE (anomalies / candidates)", anomalies, total_checked,
                "Quality control — zero anomalies means corridor is sound",
                "Throughput — checking for anomalies costs no extra compute"
            ))

        # 4. solutions per n — density
        last_n_values = [d.get("last_n", 0) for d in data if d.get("last_n")]
        if last_n_values:
            n_range = max(last_n_values)
            ratios.append(VinculumRatio(
                "SOLUTION DENSITY (solutions / n_range)", total_solutions, n_range,
                "Absolute density — solutions per integer",
                "Context — does not account for stride filtering"
            ))

        # 5. Effective span (candidates * stride)
        stride = 24
        effective_span = total_checked * stride
        ratios.append(VinculumRatio(
            "EFFECTIVE SPAN (candidates × stride)", effective_span, 1,
            "Raw search coverage — total n values spanned",
            "Efficiency — does not reflect corridor density"
        ))

        # 6. Stability index — ratio of parametric to total
        if total_solutions > 0:
            ratios.append(VinculumRatio(
                "STABILITY INDEX (parametric / total)", stable, total_solutions,
                "Parametric certainty — how many are algebraically guaranteed",
                "Discovery — ignores non-parametric solutions"
            ))

        self.ratios = ratios
        return ratios

    def suggest_next(self, ratios: list[VinculumRatio]) -> list[str]:
        """Generate navigation suggestions based on vinculum ratios."""
        suggestions = []

        hit_rate = 0.0
        anomaly_rate = 0.0
        for r in ratios:
            if "HIT RATE" in r.name:
                hit_rate = r.value
            if "ANOMALY" in r.name:
                anomaly_rate = r.value

        if hit_rate > 0.9:
            suggestions.append(
                "✓ HIGH HIT RATE — Continue current hot corridor (mod24=0, mod9∈{0,3,6}). "
                "Extend depth by 20M strides."
            )
        elif hit_rate > 0.5:
            suggestions.append(
                "→ MODERATE HIT RATE — Consider expanding to warm corridor A "
                "(mod24=0, mod9∈{1,4,7}) to test coverage."
            )
        else:
            suggestions.append(
                "⚠ LOW HIT RATE — Hot corridor may be exhausted. "
                "Suggest: expand stride to mod24∈{0,12} or try warm corridors."
            )

        if anomaly_rate > 0:
            suggestions.append(
                f"⚠ ANOMALIES DETECTED ({anomaly_rate*100:.2f}%) — "
                "Investigate anomalies before continuing. Run verification on flagged n values."
            )
        else:
            suggestions.append(
                "✓ ZERO ANOMALIES — Corridor integrity confirmed. Continue."
            )

        suggestions.append(
            "Vinculum principle: preserve hit ratio by staying in dense corridors; "
            "sacrifice coverage for confidence. Expand only when hit rate drops below 50%."
        )

        self.suggestions = suggestions
        return suggestions

    def generate_plan(self) -> str:
        """Generate a full vinculum navigation plan from current outputs."""
        outputs = self.load_outputs()
        if not outputs:
            return "No sieve output files found. Run the sieve first."

        ratios = self.compute_ratios(outputs)
        suggestions = self.suggest_next(ratios)

        lines = []
        lines.append("# Vinculum Navigation Plan")
        lines.append(f"**Generated:** {datetime.now().isoformat()}")
        lines.append("")
        lines.append("## Current Vinculum Ratios")
        lines.append("")
        lines.append("| Ratio | Value | Preserves | Sacrifices |")
        lines.append("|-------|-------|-----------|------------|")
        for r in ratios:
            pct = r.value * 100
            lines.append(f"| {r.name} | {r.value:.6f} ({pct:.2f}%) | {r.preserves} | {r.sacrifices} |")
        lines.append("")
        lines.append("## Navigation Suggestions")
        lines.append("")
        for s in suggestions:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("## Recommended Next Step")
        lines.append("")

        hit_rate = next((r.value for r in ratios if "HIT RATE" in r.name), 0)
        if hit_rate > 0.9:
            lines.append("```bash")
            # Find the last v and suggest next chunk
            last_v = max(
                (d.get("last_n", 0) for d in outputs if d.get("last_n")),
                default=0
            )
            next_v = last_v + 1 if last_v > 0 else 32000000
            lines.append(f"python sieve_l40s_hot_corridor.py --v {next_v} --depth 20833333")
            lines.append("```")
        elif hit_rate > 0.5:
            lines.append("Consider running a warm corridor sweep to test coverage:")
            lines.append("```bash")
            lines.append("python warm_corridor_sweep.py --mod9 1,4,7 --start 1 --end 10000000")
            lines.append("```")
        else:
            lines.append("Hot corridor may be depleted. Consider:")
            lines.append("- Expanding stride to include mod24 ∈ {0, 12}")
            lines.append("- Running the cold corridor sampler")
            lines.append("- Reviewing anomaly log for structural feedback")

        lines.append("")
        lines.append("---")
        lines.append("*Generated by vinculum_navigator.py — the ratio drives the search*")

        return "\n".join(lines)


# ─── CLI ───

def main():
    nav = VinculumNavigator()
    plan = nav.generate_plan()
    print(plan)

    out_path = nav.base_dir / "VINCULUM_NAV_PLAN.md"
    out_path.write_text(plan)
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
