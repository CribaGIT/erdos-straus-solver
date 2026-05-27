# erdos-straus-solver

**Part of the MANIFOLD field computation system.**  
**Copyright (c) 2026 Guinea Pig Trench LLC**

---

Erdos-Straus hot corridor sieve — integer solver, stride-24, 100% hit rate.

## Architecture

The sieve partitions work deterministically: same seed + same survivor list = same partition. This is the **parallel transport** of number theory problems across compute nodes — the manifold geometry of the solution space.

## Quick Start

```bash
git clone https://github.com/COMMENCINGTHESCOURGE/erdos-straus-solver.git
python sieve-daemon.py survivors.txt --threads 8
```

## Entity

| Field | Value |
|-------|-------|
| Copyright | Guinea Pig Trench LLC |
| R&D Entity | Guinea Pig Trench LLC (PA, #13674084) |
