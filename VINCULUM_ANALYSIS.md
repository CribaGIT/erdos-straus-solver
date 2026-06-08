# Vinculum Analysis: Erdos-Straus Conjecture

## The Central Vinculum

```
      4/n
    ───────
  1/x + 1/y + 1/z
```

The conjecture itself is a vinculum. The TOP is the target (a rational), the BOTTOM is the decomposition (a sum of three unit fractions), and the BAR is equality — "can every rational `4/n` be expressed this way?"

The orange peel question: **what does representing `4/n` as three unit fractions preserve, and what does it sacrifice?**

---

## What the Egyptian Fraction Form Preserves

| Property | How it's preserved |
|---|---|
| **Denominator structure** | Each term `1/k` is irreducible — a single integer denominator with numerator 1 |
| **Integer arithmetic** | `4xyz = n(xy + xz + yz)` is purely multiplicative — no floating point, no approximations |
| **Ordering** | `x ≤ y ≤ z` is enforced, giving a canonical form to every solution |
| **Composability** | Solutions can be combined, nested, or parametrically generated |

---

## What the Egyptian Fraction Form Sacrifices

| Property | How it's sacrificed |
|---|---|
| **Uniqueness** | Multiple `(x,y,z)` exist for the same `n`. The representation is not unique — the vinculum captures *a* ratio, not *the* ratio |
| **Closure** | Not all `n` have a known decomposition. The vinculum is conjectured, not proven |
| **Simplicity** | `4/n` is simpler than `1/x + 1/y + 1/z`; the Egyptian form is strictly longer |
| **Boundedness** | `x,y,z` can be much larger than `n`; there is no bound on denominator size |

---

## The Four Vinculum Roles in Erdos-Straus

### DIVISION — `operand / operator`

The core structure: `4/n` is a division. Each `1/x` is a division. The equation statement `4/n = ...` is an assertion that two divisions are equal.

```text
  4 / n    =   1 / x  +  1 / y  +  1 / z
 dividend / divisor   unit_fraction / denominator
```

### GROUPING — `context / symbol`

The three-term sum `(1/x + 1/y + 1/z)` groups individual unit fractions into a collective. The vinculum over the group says "these three together equal the target."

```text
  ( 1/x + 1/y + 1/z )   grouped sum
  ────────────────────
          4/n           target
```

The identity solutions also use grouping:
- `n=4k → (3k + 3k + 3k)` — all three terms equal, maximum symmetry
- `n=3k → (2k + 2k + n)` — two equal, one different

### MULTIPLICATION — `factor / product`

Parametric families are scaling vinculums:

```text
    n=4k              n=3k
  ────────────     ────────────
  (3k,3k,3k)      (2k,2k,n)
```

The factor `k` scales the entire solution. The vinculum preserves the ratio across scaling — if `n` doubles, the solution structure scales accordingly.

The hot corridor itself is a multiplicative vinculum:

```text
  stride-24       mod-9 classification
  ──────────  ×   ────────────────────
     n             STABLE / BREACH / NEUTRAL
```

Only `n` where `n mod 24 = 0` AND `n mod 9 ∈ {0,3,6}` produce the "breach" density.

### REPETITION — `pattern / period`

Modular arithmetic creates repeating patterns:

```text
  n mod 24   →   0 = hot corridor (stride-24)
  n mod 9    →   {0,3,6} = breach corridor (period-3 within 24)
  n mod 4    →   0,1,2,3 = different parametric families
```

The conjecture itself is a periodic vinculum: it repeats for every `n`, asking the same question. The pattern of which residues admit trivial parametric solutions (n mod 4 = 0, n mod 3 = 0) and which require deeper search (n mod 4 = 1) is a periodicity in the solution space.

---

## Solver Architectures as Vinculums

### Omega Solver — `divisor_search / congruence_filter`

```text
          divisor_search on x
    ────────────────────────────────
    (x = (n+A)/4, A=4m+3, d|x, d≡-nx mod A)
```

- **Preserves**: Deterministic completeness for given A range. For each `A`, the divisor search finds ALL `(d, x)` pairs satisfying the congruence.
- **Sacrifices**: The number of divisors grows with `x`; for large `A`, `x` grows, and the search becomes expensive. The `A` parameter itself is searched linearly (`m` from `0` to `max_harmonics`), which is brute force — the vinculum does not know which `A` will work.

### Bradford Solver — `parametric_covering / modular_condition`

```text
          parametric (k,ell) family
    ────────────────────────────────
    (p satisfies congruence for lemma)
```

- **Preserves**: Parametric insight — if `p` fits the congruence, the solution is immediate and algebraic. No search needed at the `(x,y,z)` level.
- **Sacrifices**: The congruence condition is restrictive. For many `n`, no `(k,ell)` within reasonable range produces a hit. The covering system must be dense enough to catch all `n`, which is unproven.

### The Squareful Barrier — `squareful_n / parametric_seed`

```text
      p²|n for every p|n
    ────────────────────
    Bradford congruence
```

The Bradford parametric system requires at least one prime factor `p` where `p ∥ n` (p divides n exactly once — exponent exactly 1). This prime seeds the congruence `k(4n-ell) ≡ ell mod A`. When every prime exponent ≥ 2 (n is squareful), no seed exists and Bradford cannot resolve the vinculum.

This is a **structural boundary** in the solution manifold:

- **Preserves**: The distinction between primitive and repeated prime factors — the vinculum encodes the algebraic requirement that Bradford's lemmas need a primitive residue class
- **Sacrifices**: Coverage on squareful numbers — the entire class of "perfect power" representations is invisible to the parametric method
- **Cross-domain**: Maps to HARD_SEAM in the terrain engine — some regions of the solution space require a fundamentally different traversal strategy

### The Delta — `Omega / Bradford`

```text
       Omega solution (x,y,z)
    ──────────────────────────
    Bradford solution (x,y,z)
```

The delta analysis shows these are DIFFERENT vinculums for the same `n`. They agree on `A = 4m+3` and `x = (n+A)/4`, but diverge in `y` and `z`. This means:

- The vinculum `4/n = 1/x + 1/y + 1/z` has **more than one resolution** for the same `n`
- Neither resolution is "the" solution — they are different ratios that happen to equal the same target
- This is the orange peel of non-uniqueness: multiple vinculums can equal the same TOP without agreeing on BOTTOM

---

## Cross-Domain Mappings

| Erdos-Straus | Hyperpoly Terrain | What it maps |
|---|---|---|
| `4/n = 1/x + 1/y + 1/z` | `V(x) = Σ a_n Φ_n(x)` | Target / decomposition vinculum |
| Stride-24 pattern | WRAP_SEAM periodicity | Repetition role — modular structure |
| Mod-9 classification | conservation_domain (STRICT/SOFT/NONE) | Classification vinculum — what gets which treatment |
| Hot corridor | LOD priority | Optimization boundary — search where signal is |
| `n mod 4 = 0` identity | `Axiom 1: Darcy flux is sufficient` | Zero-cost solution — guaranteed by structure |
| Omega solver (search) | pass1_culling (culling) | Search / filter — discard unpromising areas |
| Bradford solver (parametric) | phase5_stitch (LOD snapping) | Parametric / approximate — use structure when available |
| Delta analysis | PREDICTION_LEDGER | Comparative measurement — how different approaches diverge |
| `n = 1 mod 4` hard case | HARD_SEAM on Y axis | Hard boundary — no analytical shortcut; requires search |
| Squareful barrier | HARD_SEAM on Y axis | Structural barrier — parametric method cannot cross; requires different solver |
| Non-squareful bridge | WRAP_SEAM on X axis | Both solvers can cross — parametric and search agree on existence, disagree on form |

---

### The Constraint Correction — `d|x → d|nx²`

The original Omega solver imposed `d | x`. This was too restrictive — the correct constraint is `d | nx²`.

```text
       d|x         d|nx²
    ───────── → ──────────
    divisor of x  divisor of nx²
```

This is itself a vinculum: what was thought to be a necessary condition (`d|x`) was actually a sufficient-but-not-necessary constraint. Relaxing it to `d|nx²` preserves all previously found solutions while adding new ones (e.g., n=2521).

- **Preserves**: All existing solutions remain valid. The constraint relaxation is a strict superset.
- **Sacrifices**: Performance — the search space grows from `tau(x)` to `sum_{g|nx} tau(g)`. Measured: 37x slower (243 us vs 6.6 us per n), but still 0.1s for 416 values.
- **Cross-domain**: Maps to Axiom 5 in VISION.md — "every deformation is local" was silently assuming a stronger constraint than the math requires.

---

## The Orange Peel Summary

The Erdos-Straus conjecture, viewed through the vinculum lens:

- **What the Egyptian fraction representation preserves**: Integer exactness, unit-fraction structure, composability
- **What it sacrifices**: Uniqueness, closure, boundedness, simplicity
- **What the hot corridor preserves**: Search efficiency — 100x speedup in known corridors
- **What the hot corridor sacrifices**: Coverage guarantee — solutions outside corridors may be missed if the solver stops at corridor boundaries
- **What parametric identities preserve**: Zero-cost solutions for specific residue classes
- **What parametric identities sacrifice**: Generality — they do not cover all `n`
- **What the Omega solver preserves**: Search completeness within its parameter range
- **What the Omega solver sacrifices**: Structural insight — it finds solutions without explaining why they exist
- **What the Bradford solver preserves**: Algebraic structure — the solution is derived, not found
- **What the Bradford solver sacrifices**: Coverage — the parametric families are incomplete
