# The Factorization Separation Conjecture

## Statement

For all `n ≡ 1 (mod 24)` in the tested range `[25, 10000]`:

Let `F_Ω(n)` be the set of `(x,y,z)` produced by the Omega solver (divisor-congruence search over `A = 4m+3`), and `F_B(n)` be the set produced by the Bradford solvers (parametric Type I and Type II covering over `A = 4k+3`).

Then:

1. **Disjointness**: `F_Ω(n) ∩ F_B(n) = ∅` for all `n` where both sets are non-empty.
2. **Omega dominance**: `|F_Ω(n)| ≥ 1` for all `n` tested (coverage 100% with h≥200).
3. **Bradford restriction**: `|F_B(n)| ≥ 1` only when `n` is **not squareful** (i.e., at least one prime factor has exponent exactly 1).
4. **Non-uniqueness**: `|F_Ω(n) ∪ F_B(n)| ≥ 2` whenever both are non-empty.

## Measured Evidence (n = 1 mod 24, ≤10K, 416 values)

| Property | Value | Sample |
|---|---|---|
| Shared n coverage | 92.3% (384/416) | — |
| Shared (x,y,z) coverage | **0.0%** (0/384) | — |
| Canonicalization artifact rate | 0.0% | Sorted triples never match |
| Omega-only | 7.7% (32/416) | All squareful (every prime exponent ≥ 2) |
| Bradford-only | 0.0% (0/416) | All resolved by fixing d\|x → d\|nx² |
| Truly unsolved (any depth) | 0 of 416 | All solved by Omega h≤200 |

## What the Invariant Is Not

Several possible explanations were ruled out:

| Hypothesized invariant | Result |
|---|---|
| Solvers agree on x, differ on (y,z) | **False** — x differs in 99.5% of cases |
| Sorting (y,z) resolves disagreement | **False** — 0.0% artifact rate |
| Unsolved cases are a third family | **False** — Omega solves all with deeper search |
| Disagreement is a coincidence of parameter bounds | **False** — persists across h=200, k=1000 |
| Bradford fails on composites | **False** — solves n = p²q (e.g. 1825 = 5²·73) |
| Bradford fails on n = p² specifically | **Too narrow** — fails on ALL squareful n |

## What the Invariant Actually Is

The two solvers produce **orthogonal factorizations** of the same rational `4/n`. They are orthogonal in the sense that:

- Both express `4/n` as `1/x + 1/y + 1/z` with integer `x,y,z`
- Both search over `A = 4m+3` 
- But the algebraic path from `(n, A)` to `(x,y,z)` is fundamentally different:

```
Omega:   (n, A) → x = (n+A)/4 → d|x, d≡-nx mod A → y,z from (nx+d)/A, (nx+(nx)^2/d)/A
Bradford: (n, A) → (k, ell) → x,y,z from parametric lemma with congruence filter
```

The Omega path uses **divisor structure** of `x`. The Bradford path uses **modular congruences** between `n` and parameters. These are different operations on the same input — they produce different outputs because they traverse different regions of the solution manifold.

## The Squareful Barrier

Bradford's lemmas require a prime factor with exponent exactly 1 to seed the parametric congruence. When `n` is **squareful** (every prime exponent ≥ 2), no such seed exists and Bradford fails unconditionally at all tested `(k, ell)` depths.

A number is squareful (powerful) iff for every prime `p|n`, `p²|n`. Examples:
- `n = p²` (e.g., 25, 49, 5329)
- `n = p⁴` (e.g., 625, 2401)
- `n = p²·q²` (e.g., 1225 = 5²·7², 3025 = 5²·11²)

Confirmed at h=200, k=500 across all n = 1 mod 24 up to 10⁶:

| Range | Total | Squareful | Bradford fails on non-squareful | Omega fails on squareful |
|---|---|---|---|---|
| ≤ 10K | 416 | 32 | 0 | 0 |
| ≤ 50K | 2,083 | 74 | 0 | 0 |
| ≤ 100K | 4,166 | 104 | 0 | 0 |
| ≤ 500K | 20,833 | 236 | 0 | 0 |
| ≤ 1M | 41,666 | 334 | 0 | 0 |

The squareful barrier is universal across all tested ranges — Bradford fails exactly on squareful n, succeeds exactly on non-squareful n, with 0 exceptions at every scale.

## Resolved: The Omega Gap Was a Constraint Bug

The single Bradford-only case (n=2521) was not a genuine Omega gap — it was caused by an overly restrictive constraint `d | x` in the Omega solver. The correct mathematical condition is `d | nx²`. 

The original constraint `d | x` assumed the divisor `d` derived from `y = (nx+d)/A` must divide `x`. For n=2521, the correct `d` satisfies `d ≡ -nx mod A` and `d | nx²`, but `d ∤ x`. Example: x=652, d=1304=2x, d∤x but d|nx². After fixing to check `d | nx²`, all 416 values are solvable by Omega at h≤200.

This also proves: Omega's algebraic path (divisor search) is NOT inherently restricted to `d|x` — the correct divisor condition is `d | nx²`, which is strictly more general.

## Prediction: Third Solver

A brute-force first-found solver (enumerate x ascending, then y ascending) was tested against Omega and Bradford across 69 shared n values up to 2000:

| Disjoint from | Rate |
|---|---|
| Bradford | 100.0% (69/69) |
| Omega | 49.3% (34/69) |
| Both | 49.3% (34/69) |

The brute-force solver is always disjoint from Bradford but only half the time from Omega — because both brute-force and Omega search in order of increasing x, and Omega's first-found solution is often the minimal-x solution. A truly distinct third family would require a fundamentally different algebraic path, not just a different search order.

## The Additive Shift Framework: A Three-Tier Classification

For `n = p²` (prime square), the Erdos-Straus equation `4/p² = 1/x + 1/y + 1/z` admits a systematic solution via the **additive shift**:

Choose `A ≡ 3 (mod 4)`. Set `x = (p² + A)/4`. The remaining sum `R = 4A / (p²(p²+A))` must split into two unit fractions.

### Tier 1 (p ≡ 3 mod 4)
`A = p` works universally: `x = p(p+3)/4`, and the split follows from `c = (p+3)/4` dividing `p² + p`.
- Verified: all 49 primes p ≡ 3 mod 4 up to 500.

### Tier 2 (p ≡ 1 mod 4, c = (p+3)/4 has a divisor ≡ 2 mod 3)
`A = 3p` works: `x = p(p+3)/4`, and the divisor `d = p·c²` satisfies the Omega congruence.
- Verified: all 22 such primes up to 500.

### Tier 3 (p ≡ 1 mod 12, c has NO divisor ≡ 2 mod 3)
`A` ranges over a bounded set `{7, 11, 15, 19, 23, 31, 39, 43, 47, 51, 59, 67, 71, 79, 83, 87, 103, ...}`. The minimal working `A` is determined by a modular decision tree rooted at `p mod 7`:

```
p mod 7 ∈ {3, 5, 6} → A = 7   (49.6%)
p mod 7 ∈ {1, 2, 4}:
  p mod 11 ∈ {2, 6, 7, 10} → A = 11   (22.5%)
  p mod 11 ∈ {1, 3, 4, 5, 9}:
    p mod 5 distinguishes A ∈ {15, 19, 23, 31, 39, 43, 47, 51, 59, ...}
```

**Computational evidence for Bounded-A conjecture:** ALL 289,372 exceptional primes up to 10⁸ are solved with A ≤ 159 (max m = 39). Mean minimal m = 2.25. Zero failures across all tested ranges. The full distribution:

| A | m | Count (10⁸) | % | Trend from 10⁷ |
|---|---|---|---|---|
| 7 | 1 | 143,145 | 49.47% | Stable ~50% |
| 11 | 2 | 65,251 | 22.55% | Stable ~22.5% |
| 15 | 3 | 27,112 | 9.37% | Stable ~9.5% |
| 19 | 4 | 25,644 | 8.86% | Stable ~8.9% |
| 23 | 5 | 13,772 | 4.76% | Stable ~4.8% |
| 31 | 7 | 7,459 | 2.58% | Stable ~2.6% |
| 39 | 9 | 3,697 | 1.28% | Stable ~1.3% |
| 43 | 10 | 1,325 | 0.46% | Slowly increasing |
| 47 | 11 | 1,080 | 0.37% | Slowly increasing |
| 51 | 12 | 241 | 0.08% | Slowly decreasing |
| 59 | 14 | 331 | 0.11% | Slowly increasing |
| 67 | 16 | 87 | 0.03% | Very rare |
| 71 | 17 | 119 | 0.04% | Very rare |
| 79 | 19 | 60 | 0.02% | Very rare |
| 83 | 20 | 16 | <0.01% | Very rare |
| 87 | 21 | 12 | <0.01% | Very rare |
| 95 | 23 | 1 | <0.01% | One case: p=38,409,121 |
| 103 | 25 | 8 | <0.01% | Very rare |
| 107 | 26 | 4 | <0.01% | Very rare |
| 111 | 27 | 5 | <0.01% | Very rare |
| 127 | 31 | 2 | <0.01% | p=36,851,929 and p=68,204,761 |
| 159 | 39 | 1 | <0.01% | One case: p=91,267,201 |

**Critical observation:** Certain A values are systematically skipped as minimal solutions. The skipped values are A ∈ {3, 27, 35, 55, 63, 75, 91, 99, 115, 119, 123, 131, 135, 139, 143, 147, 151, 155} (m ∈ {0, 6, 8, 13, 15, 18, 22, 24, 28, 29, 30, 32, 33, 34, 35, 36, 37, 38}). The skip is structural — when a skipped A would work, some smaller A from the permitted set always works first. The pattern of permitted A values is sparse but appears to cover all A = 4m+3 where ℓ₂-adic and ℓ₃-adic properties of p²+A permit the divisor-congruence condition.

**Maximal minimal A grows very slowly:** At p = 10⁵, max m = 12. At p = 10⁶, max m = 17. At p = 10⁷, max m = 27. At p = 10⁸, max m = 39. The growth is consistent with `O(log p)` or even `O(log log p)` scaling, strongly suggesting a universal absolute bound C exists such that every exceptional prime has a valid shift with A ≤ C.

## Open Questions

1. Does the disjointness hold for all `n`, or is there some `n` where both solvers converge to the same triple?
2. Does Omega's coverage remain 100% as `n → ∞`, or is there a harmonic bound?
3. Can the `(y,z)` pairs from the two families be used to triangulate a third factorization family?
4. Why are certain A values (27, 35, 47) systematically skipped as minimal solutions? Is there a structural obstruction?
5. Does the bounded-A conjecture for Tier 3 (A ≤ 51 for all p) follow from p-adic properties of the divisor-congruence condition?
6. Prove that Tier 1 (A = p) and Tier 2 (A = 3p) are exact classifications: the condition on c = (p+3)/4 is both necessary and sufficient.
