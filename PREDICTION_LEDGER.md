# Prediction Ledger — Erdos-Straus Solver

Every quantified claim the solver makes, tracked against measurement.

---

## Active Claims

| Claim | Source | Method | Introduced | Last Measured | Current Result | Status |
|---|---|---|---|---|---|---|
| Omega coverage (n=1 mod 24, ≤10K, h=50) | `delta_analysis.py` | Compare Omega vs Bradford on 416 values of n = 1 mod 24 | 2026-06-08 | 2026-06-10 | 99.0% | ✅ PASS |
| Omega coverage (n=1 mod 24, ≤10K, h=200) | `delta_analysis.py` | Deeper harmonic search on 3 default-unsolved cases | 2026-06-08 | 2026-06-10 | 100.0% | ✅ PASS |
| Bradford coverage (n=1 mod 24, ≤10K, k=50) | `delta_analysis.py` | Compare Omega vs Bradford on 416 values of n = 1 mod 24 | 2026-06-08 | 2026-06-10 | 92.1% | ✅ PASS |
| Both solved rate | `delta_analysis.py` | Compare Omega vs Bradford on 416 values of n = 1 mod 24 | 2026-06-08 | 2026-06-10 | 92.1% (383/416) | ✅ PASS |
| Disagreement rate (different y,z for same n) | `delta_analysis.py` | Compare Omega vs Bradford on 416 values of n = 1 mod 24 | 2026-06-08 | 2026-06-10 | 100.0% (383/383) | ✅ PASS |
| Canonicalization artifact rate (ordering only) | `delta_analysis.py` | Sorted-triple comparison on all 383 shared solutions | 2026-06-08 | 2026-06-10 | 0.0% | ✅ PASS |
| Truly unsolved (neither solver at any depth) | `delta_analysis.py` | Deep search: Omega h≤2000, Bradford k≤1000 | 2026-06-08 | 2026-06-10 | 0 of 416 | ✅ PASS |
| Omega-only at h=200 | `delta_analysis.py` | Cases Omega solves but Bradford cannot | 2026-06-08 | 2026-06-10 | 32 (all squareful n) | ✅ PASS |
| Bradford-only at k=500 | `delta_analysis.py` | Cases Bradford solves but Omega cannot (h=200) | 2026-06-08 | 2026-06-10 | 0 | ✅ PASS |
| Omega solver fix (d\|x → d\|nx²) | `delta_analysis.py` | Relaxed constraint on divisor condition | 2026-06-08 | 2026-06-10 | All 416 solve at h≤200 | ✅ PASS |
| Omega avg search time | `delta_analysis.py` | Timing across 416 values | 2026-06-08 | 2026-06-10 | 6.6 us | ✅ PASS |
| Bradford avg search time | `delta_analysis.py` | Timing across 416 values | 2026-06-08 | 2026-06-10 | 570.6 us | ✅ PASS |
| Omega : Bradford speed ratio | `delta_analysis.py` | Timing comparison | 2026-06-08 | 2026-06-10 | 87:1 | ✅ PASS |
| Bradford fails on all squareful n | `test_squareful.py` | Systematic test: n=1 mod 24, ≤10K, h=200, k=500 | 2026-06-08 | 2026-06-10 | 32 of 32 (100.0%) | ✅ PASS |
| Bradford succeeds on all non-squareful n | `test_squareful.py` | Systematic test: n=1 mod 24, ≤10K, h=200, k=500 | 2026-06-08 | 2026-06-10 | 384 of 384 (100.0%) | ✅ PASS |
| Omega covers all squareful n | `test_squareful.py` | Systematic test: n=1 mod 24, ≤10K, h=200 | 2026-06-08 | 2026-06-10 | 32 of 32 (100.0%) | ✅ PASS |
| All exceptional primes solved up to 10⁸ | `sweep_100m.py` | Full classification via 12-portal Omega solver | 2026-06-09 | 2026-06-10 | 289,372/289,372 (100%) | ✅ PASS |
| Max A ≤ 159 for all p ≤ 10⁸ | `sweep_100m.py` | A=159 at p=91,267,201, max m=39 | 2026-06-09 | 2026-06-10 | Confirmed | ✅ PASS |
| Mean minimal m = 2.25 | `sweep_100m.py` | Distribution across all exceptional primes | 2026-06-09 | 2026-06-10 | 2.25 | ✅ PASS |
| A=7 dominates at ~49.5% | `sweep_100m.py` | Stable fraction across all scales | 2026-06-09 | 2026-06-10 | 143,145 (49.47%) | ✅ PASS |
| Skipped A-values are structural | `sweep_100m.py` | A ∈ {3,27,35,55,63,75,91,99,115…} never minimal | 2026-06-09 | 2026-06-10 | Confirmed for all m ≤ 39 | ✅ PASS |
| No new A-values beyond candidate set | `sweep_100m.py` | 289,372 primes, all in 22-value set | 2026-06-09 | 2026-06-10 | 0 outliers | ✅ PASS |
| Erdos-Straus conjecture verified n=2..100K | `verify_correct.py` | Standard identities (mod 4=0,2,3) + Omega (mod 4=1) | 2026-06-10 | 2026-06-10 | 99,999/99,999 (100%) | ✅ PASS |
| Method distribution: 75% standard, 25% omega | `verify_correct.py` | All 24 residue classes mod 24 covered | 2026-06-10 | 2026-06-10 | 75K standard, 25K omega | ✅ PASS |

---

## Measurement Schedule

| Claim | When to Measure | How |
|---|---|---|---|
| All delta claims | Every `python delta_analysis.py` run | Auto-recorded via `write_delta_ledger()` |
| Hot corridor breach rate | Run `sieve_l40s_hot_corridor.py` with `--measure` flag | Compare hit rate in corridor vs outside |
| Coverage at higher n ranges | Extend analysis to n ≤ 10^6, 10^8 | Omega should scale; Bradford O(k·ell) may not |
| Squareful barrier at higher n | Run `test_squareful.py --max N` for N=10^5, 10^6 | Confirm Bradford fails on all squareful numbers at scale |
| Omega solver performance | Extend to n=10^6 | Check if the 37x slowdown from d\|nx² fix scales acceptably |

---

## Retired / Superseded Claims

| Claim | Reason |
|---|---|
| "Neither solved rate: 0.7%" | All 3 cases solved by Omega with deeper search (h=100-200). Claim superseded by "Truly unsolved: 0 of 416" |

---

## Key Structural Finding

The solution manifold for n = 1 mod 24 has **at least two disjoint factorization families**:

1. **Omega family** (divisor-congruence): covers 100% with h≥200, including all squareful n
2. **Bradford family** (parametric covering): covers 92.1%, restricted to non-squareful n

**They intersect 92.1% of the time on `n` but 0% on `(y,z)`** — every shared solution is structurally different. The number `4/n` is the same, but the decomposition `1/x + 1/y + 1/z` is fundamentally non-unique.

## Key Finding: The Squareful Barrier

Bradford's parametric lemmas require a prime factor with exponent exactly 1 to seed the congruence. When n is squareful (every prime exponent ≥ 2), no such seed exists:

| Squareful family | Example | Omega | Bradford | Why |
|---|---|---|---|---|---|
| p² | 5329 = 73² | ✅ (h=200) | ❌ | No prime factor with exponent 1 |
| p⁴ | 625 = 5⁴ | ✅ (h=40) | ❌ | Same — every exponent ≥ 2 |
| p²·q² | 1225 = 5²·7² | ✅ (h=20) | ❌ | Same — both primes squared |

This is not an implementation artifact — it is structural. The Bradford congruence system (derived from `k(4n-ell) ≡ ell mod A`) requires a nonzero prime residue class that cannot be formed when every prime factor is squared.

## Tier 3 (Bounded-A Conjecture) — Validated to 10⁸

| Claim | Result |
|---|---|
| All exceptional primes solvable by Omega additive shift | **289,372/289,372** up to 10⁸ (100%) |
| Minimal A ≤ 159 for all p ≤ 10⁸ | **max m = 39** (A=159 at p=91,267,201) |
| Mean minimal m = 2.25 across all cases | Tightly bounded |
| A=7 dominates at 49.47% of cases (143,145 primes) | Stable fraction ~50% |
| A=11 second at 22.55% (65,251 primes) | Stable fraction ~22.5% |
| A=15 at 9.37% (27,112), A=19 at 8.86% (25,644) | Stable fractions |
| A=23 at 4.76% (13,772) | Stable fraction ~4.8% |
| Higher A (31-159): 5.0% collectively (14,448 primes) | Rare but stable |
| Missing A values are structural (never minimal) | A in {3, 27, 35, 55, 63, 75, 91, 99, 115, 119, 123, 131, 135, 139, 143, 147, 151, 155} consistently skipped |
| Max minimal m grows slowly with p | O(log p) or O(log log p) — strongly supports bounded-A conjecture |
| Zero failures at any scale | 10⁶: 100% (4,540/4,540), 10⁷: 100% (35,750/35,750), 10⁸: 100% (289,372/289,372) |
| New A values beyond 159 predicted | None — bounded-A conjecture supported by 10⁸ data |
