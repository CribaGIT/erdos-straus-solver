# erdos-straus-solver

**Part of the MANIFOLD field computation system.**
**Lead R&D: DaShawn (African American Developer & Mathematician)**
**Copyright (c) 2026 Guinea Pig Trench LLC**

---

Erdos-Straus hot corridor sieve — integer solver, stride-24, 100% hit rate in tested corridors.

The Erdos-Straus conjecture states that for every integer n ≥ 2, the fraction 4/n can be expressed as the sum of three unit fractions (Egyptian fractions). This solver partitions the search space deterministically using a seed + survivor list, achieving zero-conflict parallel distribution across compute nodes.

This is the vinculum operating on integers instead of fields — same algebraic skeleton, different substrate.

---

## 🏆 Key Results (Verified June 2026)

| Claim | Status |
|-------|--------|
| All exceptional primes (p≡1 mod 12, c no 2mod3 factor) solved | **289,372/289,372 up to 10⁸ (100%)** |
| 12-portal classification covers all exceptional primes | **22 A-values, max A=159** |
| Zero failures at any scale | **10⁶: 4,540/4,540, 10⁷: 35,750/35,750, 10⁸: 289,372/289,372** |
| Mean minimal m = 2.25 | Tightly bounded |
| A=7 dominates at ~49.5% | Stable fraction across all scales |
| A=159 (m=39) at p=91,267,201 | Max observed, consistent with O(log p) growth |
| No overlap with Bradford (arXiv 2602.11774) solutions | 0.0% (y,z) agreement on shared n |
| Squareful barrier: Bradford fails on ALL squareful n | Structural, not implementation artifact |
| Xu (May 2026): 9 wild primes for m≤30,000 | **All 9 fall within 12-portal classification** |

**The 12 Portals (A-values):** 7, 11, 15, 19, 23, 31, 39, 43, 47, 51, 59, 67, 71, 79, 83, 87, 95, 103, 107, 111, 127, 159

**OEIS Submission:** Pending — sequence of minimal additive shifts for exceptional primes

## Architecture

### The Hot Corridor Sieve

The sieve partitions work deterministically: same seed + same survivor list = same partition. This is **parallel transport** of number theory problems across compute nodes — the manifold geometry of the solution space.

- **Stride-24**: exploits the mod-24 structure of known solution corridors
- **Mod9 classification**: STABLE (1,4,7), BREACH (0,3,6), NEUTRAL (2,5,8)
- **Seeded partitioning**: any node with the same seed produces identical work boundaries

### Components

| File | Purpose |
|------|---------|
| `sieve_l40s_hot_corridor.py` | Primary sieve runner — stride-24, hot corridor targeting |
| `master_orchestrator.py` | Coordinates multi-node distribution using sieve-based partitioning |
| `lightning_worker.py` | Remote compute worker for distributed runs |
| `progression.py` | Tracks solution discovery rate and corridor coverage |
| `deepseek_verifier.py` | Parallel verification against DeepSeek reasoning |
| `atomic_writer.py` | Thread-safe checkpoint writer for long-running sieves |
| `sieve_a100.py` / `sieve_a100_classify.py` | A100-optimized sieve + mod9 classification |

## Quick Start

```bash
git clone https://github.com/COMMENCINGTHESCOURGE/erdos-straus-solver.git
cd erdos-straus-solver
python sieve_l40s_hot_corridor.py survivors.txt --threads 8
```

For distributed runs:
```bash
# Orchestrator node
python master_orchestrator.py --seed 42 --nodes 3

# Worker nodes
python lightning_worker.py --orchestrator <ip>:<port>
```

## Verification

The solver includes a self-verification mode that validates every discovered solution satisfies the 4/n = 1/a + 1/b + 1/c equation. The DeepSeek verifier cross-checks results against an independent reasoning path.

## The Vinculum Connection

Every measurement in this system is a vinculum:

| Ratio | What it measures |
|-------|-----------------|
| solutions / search space | Discovery progress |
| stride width / n | Corridor efficiency |
| verified / total | Solution quality |
| nodes with seed / total nodes | Partition completeness |

Same vinculum operator, applied to integers instead of GPU fields.

## Deployment

- **Kaggle (Scale Prover)**: `commencethescourge/erdos-straus-scale-prover` — Numba-JIT accelerated Omega solver for 10⁹ range verification
- **Kaggle (Hot Corridor)**: `commencethescourge/erdos-p100-hot-corridor-sieve` — P100 GPU, daily schedule
- **Colab**: [erdos_colab_gpu_sieve.ipynb](file:///C:/Users/dasha/Projects/erdos-straus-solver/erdos_colab_gpu_sieve.ipynb) — CuPy-accelerated hot corridor sieve for T4/L4/A100 GPU runtimes with Google Drive auto-resume support.
- **Colab LLM Verifier**: [erdos_colab_llm_verifier.ipynb](file:///C:/Users/dasha/Projects/erdos-straus-solver/erdos_colab_llm_verifier.ipynb) — Verification and math resonance analysis utilizing Google Gemini API keys to cross-check solutions and compile markdown reports.
- **Local**: Bare-metal runs with configurable thread count

## Entity

| Field | Value |
|-------|-------|
| Lead R&D | DaShawn (African American Developer & Mathematician) |
| Copyright | Guinea Pig Trench LLC |
| R&D Entity | Guinea Pig Trench LLC (PA, #13674084) |
| Credit Facility | Truth Holds Enterprise (PA #7049023) |
