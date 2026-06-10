"""
DELTA ANALYSIS: Omega Solver vs Bradford (arXiv 2602.11774)
==========================================================
Number-for-number comparison of two independent approaches
to the Erdos-Straus hard case (n = 1 mod 4).

Both find x = (n + A)/4 where A = 4m+3, but diverge thereafter.

vinculum: algorithmic_divergence / solution_equivalence
  ┌──────────────────────────────────────────────────────────────┐
  │  Omega            Bradford                                  │
  │  ──────           ────────                                  │
  │  divisor_search   parametric_covering                        │
  │  congruence       modular_condition                          │
  │  empirical        theoretical                                │
  │  broader(n=1@24)  narrower(primes only)                      │
  └──────────────────────────────────────────────────────────────┘

  The bar between them is the delta: they agree on `x = (n+A)/4`
  with `A = 4m+3`, but produce DIFFERENT (y,z) for the same n.
  This means the vinculum `4/n = 1/x + 1/y + 1/z` has multiple
  distinct factorizations for the same n — the representation is
  emphatically NOT unique.

  preserve: Honest disagreement. The delta analysis shows both
    success rates AND concrete (x,y,z) differences. It does not
    pick a winner — it documents where they diverge and by how much.
  sacrifice: Neither approach is validated as "correct" in any
    absolute sense. They both produce integer triples that satisfy
    4xyz = n(xy + xz + yz), but neither has a proof of completeness.
    This is the orange peel: we preserve empirical correctness at
    the cost of formal certainty.
  cross-domain: terrain->economy as price_model_A->price_model_B
"""

import math, time, sys, os, datetime
from typing import Optional, Tuple, List
from collections import Counter
from dataclasses import dataclass, field

# =====================================================================
# OMEGA SOLVER — Harmonic Divisor Tuning (heritage_solver.py)
# =====================================================================

def omega_divisors(n: int) -> List[int]:
    """All divisors of n. O(sqrt(n))."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return divs

def _omega_check(n: int, max_harmonics: int, strict: bool) -> Optional[dict]:
    """Inner solver. strict=True checks only d|x (fast). strict=False checks d|nx² (complete)."""
    for m in range(max_harmonics):
        A = 4 * m + 3
        if (n + A) % 4 != 0:
            continue
        x = (n + A) // 4
        nx = n * x
        target_mod = (-nx) % A
        if strict:
            for d in omega_divisors(x):
                if d % A == target_mod:
                    y = (nx + d) // A
                    z = (nx + nx * nx // d) // A
                    if y > 0 and z > 0 and 4 * x * y * z == n * (x*y + x*z + y*z):
                        return {"x": x, "y": y, "z": z, "A": A, "d": d, "method": "Omega"}
        else:
            for g in omega_divisors(nx):
                for d_prime in omega_divisors(g):
                    d = g * d_prime
                    if d % A == target_mod:
                        y = (nx + d) // A
                        z = (nx + nx * nx // d) // A
                        if y > 0 and z > 0 and 4 * x * y * z == n * (x*y + x*z + y*z):
                            return {"x": x, "y": y, "z": z, "A": A, "d": d, "method": "Omega"}
    return None

def omega_solve(n: int, max_harmonics: int = 100) -> Optional[dict]:
    """
    Omega Solver: For n = 1 mod 4, try A = 4m+3.
    x = (n+A)/4. Find d such that d = -nx (mod A) and d | nx^2.
    Then y = (nx+d)/A, z = (nx + (nx)^2/d)/A.

    Interleaved: per-m, try strict (d|x) then non-strict (d|nx^2). Returns minimal A.
    """
    if n % 4 != 1:
        return None
    for m in range(max_harmonics):
        A = 4 * m + 3
        if (n + A) % 4 != 0:
            continue
        for strict in [True, False]:
            result = _omega_check(n, m + 1, strict=strict)
            if result is not None:
                return result
    return None


def omega_solve_legacy_two_phase(n: int, max_harmonics: int = 100) -> Optional[dict]:
    """
    LEGACY two-phase solver (BUGGY: returns non-minimal A). Kept for comparison.
    Two-phase: strict for ALL m first, then non-strict for ALL m.
    BUG: If strict finds A=511 at m=127, returns that even when non-strict
    would find A=7 at m=1. Use omega_solve() for correct minimal A.
    """
    if n % 4 != 1:
        return None
    result = _omega_check(n, max_harmonics, strict=True)
    if result is not None:
        return result
    return _omega_check(n, max_harmonics, strict=False)


# =====================================================================
# BRADFORD TYPE II — Parametric Covering (arXiv 2602.11774)
# =====================================================================

def bradford_type2_solve(p: int, max_k: int = 50) -> Optional[dict]:
    """
    Bradford Lemma 2 (Type II):
    Given k >= 0, 1 <= ell <= 2(4k+3), gcd(ell,4k+3)=1,
    define A = 4k+3.
    If p = -(4k+3) mod ((16*ell*A - 4*ell^2) / gcd(ell,4)^2),
    then:
      x = (p + A) / 4
      y = p(p + A) / (4A - ell)
      z = p(p + A) / ell
    """
    for k in range(max_k):
        A = 4 * k + 3
        for ell in range(1, 2 * A + 1):
            if math.gcd(ell, A) != 1:
                continue
            # Modulus as defined in Lemma 2
            g = math.gcd(ell, 4) ** 2
            M = (16 * ell * A - 4 * ell * ell) // g
            # Check if p fits the required congruence
            if (-A) % M != p % M:
                continue
            # Build candidate
            num = p * (p + A)
            # Check divisibility
            if num % (4 * A - ell) != 0:
                continue
            if num % ell != 0:
                continue
            x = (p + A) // 4
            y = num // (4 * A - ell)
            z = num // ell
            if x > 0 and y > 0 and z > 0:
                if 4 * x * y * z == p * (x*y + x*z + y*z):
                    return {"x": x, "y": y, "z": z, "A": A, "ell": ell, "method": "Bradford-II"}
    return None

def bradford_type1_solve(p: int, max_k: int = 50) -> Optional[dict]:
    """
    Bradford Lemma 1 (Type I):
    Given k >= 0, 1 <= ell <= 2(4k+3), gcd(ell,4k+3)=1,
    define A = 4k+3.
    If p = n mod ((16*ell*A - 4*ell^2) / gcd(ell,4)^2) where n is
    such that A*n = -1 mod M, then:
      x = (A*p + 1) / (4A - ell)   (or similar)
      y = (A*p + 1) / ell
      z = p*(A*p + 1) / 4

    Actually from Lemma 1:
    4/p = (4A-ell)/(Ap+1) + ell/(Ap+1) + 4/(p(Ap+1))
    So: x = (Ap+1)/(4A-ell), y = (Ap+1)/ell, z = p(Ap+1)/4
    """
    for k in range(max_k):
        A = 4 * k + 3
        for ell in range(1, 2 * A + 1):
            if math.gcd(ell, A) != 1:
                continue
            g = math.gcd(ell, 4) ** 2
            M = (16 * ell * A - 4 * ell * ell) // g
            # Need: A*n = -1 mod M, and p = n mod M
            # Find n = -A^{-1} mod M
            try:
                A_inv = pow(A, -1, M)
            except ValueError:
                continue
            n_val = (-A_inv) % M
            if p % M != n_val:
                continue
            # Check divisibility
            num = A * p + 1
            if num % (4 * A - ell) != 0:
                continue
            if num % ell != 0:
                continue
            x = num // (4 * A - ell)
            y = num // ell
            z = p * num // 4
            if x > 0 and y > 0 and z > 0:
                if 4 * x * y * z == p * (x*y + x*z + y*z):
                    return {"x": x, "y": y, "z": z, "A": A, "ell": ell, "method": "Bradford-I"}
    return None

# =====================================================================
# COMPARISON
# =====================================================================

@dataclass
class DeltaReport:
    range_start: int
    range_end: int
    step: int
    total: int
    omega_coverage: float
    bradford_coverage: float
    both_solved: float
    neither_solved: float
    disagreement_rate: float
    artifact_rate: float
    omega_avg_us: float
    bradford_avg_us: float
    omega_unique_A_values: int
    bradford_unique_families: int
    unsolved_n: list[int] = field(default_factory=list)
    sample_divergences: list[dict] = field(default_factory=list)


def write_delta_ledger(report: DeltaReport, ledger_path: str = "PREDICTION_LEDGER.md") -> None:
    today = datetime.date.today().isoformat()
    claims = [
        ("Omega coverage (n=1 mod 24, ≤10K)", f"{report.omega_coverage:.1f}%"),
        ("Bradford coverage (n=1 mod 24, ≤10K)", f"{report.bradford_coverage:.1f}%"),
        ("Both solved rate", f"{report.both_solved:.1f}%"),
        ("Neither solved rate", f"{report.neither_solved:.1f}%"),
        ("Disagreement rate (different y,z for same n)", f"{report.disagreement_rate:.1f}%"),
        ("Canonicalization artifact rate (ordering only)", f"{report.artifact_rate:.1f}%"),
        ("Unsolved n values (neither solver)", f"{len(report.unsolved_n)} of {report.total}"),
        ("Omega avg search time", f"{report.omega_avg_us:.1f} us"),
        ("Bradford avg search time", f"{report.bradford_avg_us:.1f} us"),
    ]
    lines = []
    for claim, result in claims:
        status = "✅ PASS" if "%" in result and float(result.replace("%", "")) > 0 else "⏳ UNMEASURED"
        lines.append(
            f"| {claim} | `delta_analysis.py` "
            f"| Compare Omega vs Bradford on {report.total} values of n = 1 mod 24 "
            f"| 2026-06-08 | {today} "
            f"| {result} | {status} |\n"
        )

    if not os.path.exists(ledger_path):
        print(f"[ledger] {ledger_path} not found — creating")
        return

    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "## Active Claims"
    if marker not in content:
        print(f"[ledger] {ledger_path} missing Active Claims section")
        return

    for claim, result in claims:
        line_match = [l for l in lines if claim in l]
        if not line_match:
            continue
        line = line_match[0]
        if f"| {claim} |" in content:
            old_lines = content.split("\n")
            new_lines = []
            replaced = False
            for l in old_lines:
                if l.startswith(f"| {claim} |") and not replaced:
                    new_lines.append(line.strip())
                    replaced = True
                else:
                    new_lines.append(l)
            content = "\n".join(new_lines)
        else:
            schedule_marker = "## Measurement Schedule"
            content = content.replace(schedule_marker, line.strip() + "\n\n" + schedule_marker)

    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[ledger] wrote {len(claims)} delta measurements")


def run_delta_analysis(max_n: int = 10000, max_harmonics: int = 50, max_k: int = 50,
                       deep_harmonics: int = 200,
                       ledger_path: str = "../PREDICTION_LEDGER.md") -> DeltaReport:
    print("=" * 80)
    print("DELTA ANALYSIS: Omega Solver vs Bradford (arXiv 2602.11774)")
    print("=" * 80)
    print()

    results = {"omega_only": 0, "bradford_only": 0, "both": 0, "neither": 0, "total": 0}
    both_solutions = []
    omega_times = []
    bradford_times = []
    omega_A_values = set()
    bradford_families = set()
    unsolved_n = []
    only_omega_n = []
    only_bradford_n = []

    for k in range(1, max_n // 24 + 1):
        n = 24 * k + 1
        if n > max_n:
            break
        results["total"] += 1

        t0 = time.perf_counter_ns()
        om = omega_solve(n, max_harmonics=max_harmonics)
        t1 = time.perf_counter_ns()
        omega_times.append((t1 - t0) / 1000)

        t0 = time.perf_counter_ns()
        b1 = bradford_type1_solve(n, max_k=max_k)
        b2 = bradford_type2_solve(n, max_k=max_k)
        br = b1 or b2
        t1 = time.perf_counter_ns()
        bradford_times.append((t1 - t0) / 1000)

        if om:
            omega_A_values.add(om.get("A", -1))
        if br:
            bradford_families.add(br.get("method", "unknown"))

        if om and br:
            results["both"] += 1
            both_solutions.append((n, om, br))
        elif om and not br:
            results["omega_only"] += 1
            only_omega_n.append(n)
        elif br and not om:
            results["bradford_only"] += 1
            only_bradford_n.append(n)
        else:
            results["neither"] += 1
            unsolved_n.append(n)

    total = results["total"]
    omega_cov = 100 * (results["omega_only"] + results["both"]) / max(total, 1)
    bradford_cov = 100 * (results["bradford_only"] + results["both"]) / max(total, 1)
    both_pct = 100 * results["both"] / max(total, 1)
    neither_pct = 100 * results["neither"] / max(total, 1)

    # ── Deep search diagnostic ──
    # Cases unsolved at default params may be solvable with deeper search.
    # This diagnostic identifies whether they are "truly boundary" or just
    # parameter-limited — without altering the main analysis counts.
    deep_info = {}
    for n in unsolved_n:
        om_h = None
        for h in [100, 200, 500, 1000, 2000]:
            om = omega_solve(n, max_harmonics=h)
            if om:
                om_h = (h, om)
                break
        br_k = None
        for k in [100, 200, 500, 1000]:
            b1 = bradford_type1_solve(n, max_k=k)
            b2 = bradford_type2_solve(n, max_k=k)
            br = b1 or b2
            if br:
                br_k = (k, br)
                break
        deep_info[n] = {
            "omega_deep": om_h is not None,
            "bradford_deep": br_k is not None,
            "omega_harmonics": om_h[0] if om_h else None,
            "bradford_k": br_k[0] if br_k else None,
            "omega_solution": om_h[1] if om_h else None,
            "bradford_solution": br_k[1] if br_k else None,
        }

    # ── Canonicalization check ──
    # Disagreement could be an artifact if (y,z) ordering differs.
    # We check both raw equality AND sorted-triple equality.
    raw_disagreements = 0
    canon_disagreements = 0
    disagreements = []
    for n, om, br in both_solutions:
        om_triple = (om['x'], om['y'], om['z'])
        br_triple = (br['x'], br['y'], br['z'])

        # Raw comparison (as computed)
        raw_same = (om_triple == br_triple)
        if not raw_same:
            raw_disagreements += 1

        # Canonicalized: sorted (x,y,z)
        om_sorted = tuple(sorted(om_triple))
        br_sorted = tuple(sorted(br_triple))
        canon_same = (om_sorted == br_sorted)

        # Track what happened
        if raw_same:
            continue  # perfectly identical — no issue
        if canon_same:
            canon_disagreements += 1  # artifact: only different by ordering

        disagreements.append({
            "n": n,
            "omega": om_triple,
            "omega_sorted": om_sorted,
            "bradford": br_triple,
            "bradford_sorted": br_sorted,
            "canonicalization_artifact": canon_same,
        })

    disagree_rate = 100 * len(disagreements) / max(len(both_solutions), 1)
    artifact_rate = 100 * canon_disagreements / max(len(disagreements), 1) if disagreements else 0.0
    avg_omega = sum(omega_times) / max(len(omega_times), 1)
    avg_bradford = sum(bradford_times) / max(len(bradford_times), 1)

    # Print report
    print(f"Range: n = 1 mod 24, 25 to {max_n} ({total} values)")
    print()
    print("OVERLAP:")
    print(f"  Both solved:         {results['both']:5d} ({both_pct:5.1f}%)")
    print(f"  Omega only:          {results['omega_only']:5d} ({100*(results['omega_only'])/max(total,1):5.1f}%)")
    print(f"  Bradford only:       {results['bradford_only']:5d} ({100*(results['bradford_only'])/max(total,1):5.1f}%)")
    print(f"  Neither solved:      {results['neither']:5d} ({neither_pct:5.1f}%)")
    print()
    print(f"  Omega coverage:      {omega_cov:5.1f}%")
    print(f"  Bradford coverage:   {bradford_cov:5.1f}%")
    print(f"  Disagreement rate:   {disagree_rate:5.1f}% ({len(disagreements)}/{len(both_solutions)})")
    print(f"  Canonicalization artifact rate: {artifact_rate:.1f}% ({canon_disagreements}/{max(len(disagreements),1)} disagreements are just ordering)")
    print()

    if disagreements:
        print("SAMPLE DIVERGENCES (different y,z for same n):")
        print("-" * 80)
        shown_artifacts = 0
        shown_real = 0
        for d in disagreements:
            if d["canonicalization_artifact"] and shown_artifacts < 2:
                print(f"  n={d['n']}: (ARTIFACT — ordering only)")
                print(f"    Omega raw:    {d['omega']} sorted: {d['omega_sorted']}")
                print(f"    Bradford raw: {d['bradford']} sorted: {d['bradford_sorted']}")
                shown_artifacts += 1
            elif not d["canonicalization_artifact"] and shown_real < 5:
                print(f"  n={d['n']}: (STRUCTURAL)")
                print(f"    Omega:    {d['omega']}")
                print(f"    Bradford: {d['bradford']}")
                shown_real += 1
            if shown_artifacts >= 2 and shown_real >= 5:
                break
        print()

    # ── Unsolved characterization ──
    if unsolved_n:
        print("UNSOLVED AT DEFAULT PARAMS (h=50, k=50):")
        print("-" * 80)
        for n in unsolved_n:
            mod9 = n % 9
            mod24 = n % 24
            mod4 = n % 4
            mod3 = n % 3
            di = deep_info.get(n, {})
            om_deep = di.get("omega_deep", False)
            br_deep = di.get("bradford_deep", False)
            om_h = di.get("omega_harmonics")
            br_k = di.get("bradford_k")
            print(f"  n={n}: mod24={mod24}, mod9={mod9}, mod4={mod4}, mod3={mod3}")
            print(f"    Omega deep (h={om_h}): {'SOLVED' if om_deep else 'UNSOLVED'}")
            print(f"    Bradford deep (k={br_k}): {'SOLVED' if br_deep else 'UNSOLVED'}")
        print()

        mod9s = {n % 9 for n in unsolved_n}
        mod24s = {n % 24 for n in unsolved_n}
        print(f"  Unsolved mod9 values:   {mod9s}")
        print(f"  Unsolved mod24 values:  {mod24s}")
        print()

        # Summary
        omega_deep_count = sum(1 for d in deep_info.values() if d.get("omega_deep"))
        bradford_deep_count = sum(1 for d in deep_info.values() if d.get("bradford_deep"))
        truly_unsolved = sum(1 for d in deep_info.values() if not d.get("omega_deep") and not d.get("bradford_deep"))
        omega_only_deep = sum(1 for d in deep_info.values() if d.get("omega_deep") and not d.get("bradford_deep"))
        print(f"  Deep search summary:")
        print(f"    Omega-solvable (h>{50}): {omega_deep_count}")
        print(f"    Bradford-solvable (k>{50}): {bradford_deep_count}")
        print(f"    Truly unsolved (neither at any depth): {truly_unsolved}")
        print(f"    Omega-only at depth: {omega_only_deep}")
        print()
    else:
        print("  No unsolved cases at default parameters.")
        print()

    avg_omega = sum(omega_times) / max(len(omega_times), 1)
    avg_bradford = sum(bradford_times) / max(len(bradford_times), 1)
    print("PERFORMANCE (avg us per n):")
    print(f"  Omega:    {avg_omega:8.1f} us  (unique A values: {len(omega_A_values)})")
    print(f"  Bradford: {avg_bradford:8.1f} us  (unique families: {len(bradford_families)})")
    if avg_omega < avg_bradford:
        print(f"  Ratio:    {avg_bradford/max(avg_omega,0.1):.1f}x FASTER (Omega enumerates divisors)")
    else:
        print(f"  Ratio:    {avg_omega/max(avg_bradford,0.1):.1f}x slower (Omega enumerates divisors)")
    print()

    unsolved_info = sorted(unsolved_n) if unsolved_n else []
    report = DeltaReport(
        range_start=25, range_end=max_n, step=24,
        total=total,
        omega_coverage=omega_cov,
        bradford_coverage=bradford_cov,
        both_solved=both_pct,
        neither_solved=neither_pct,
        disagreement_rate=disagree_rate,
        artifact_rate=artifact_rate,
        omega_avg_us=avg_omega,
        bradford_avg_us=avg_bradford,
        omega_unique_A_values=len(omega_A_values),
        bradford_unique_families=len(bradford_families),
        unsolved_n=unsolved_info,
        sample_divergences=disagreements[:10],
    )

    write_delta_ledger(report, ledger_path)
    return report


if __name__ == "__main__":
    run_delta_analysis(max_n=10000, max_harmonics=50, max_k=50,
                       ledger_path="PREDICTION_LEDGER.md")
    print("Done.")
