"""Benchmark optimized two-phase Omega solver."""
import sys, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

# Verify correctness
print("=== Correctness check ===")
n = 2521
om = omega_solve(n, max_harmonics=200)
print(f"n={n}: Omega={'FOUND' if om else 'NOT FOUND'} (A={om['A']}, x={om['x']}, d={om['d']})")

# All n up to 10000
fails = []
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    om = omega_solve(n, max_harmonics=200)
    if not om: fails.append(n)
print(f"Omega fails at h=200 on {len(fails)} values: {fails}")

fails = []
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    br = bradford_type1_solve(n, max_k=500) or bradford_type2_solve(n, max_k=500)
    if not br: fails.append(n)
print(f"Bradford fails at k=500 on {len(fails)} values: {fails}")

# Benchmark
print("\n=== Performance benchmark ===")
total_time = 0
count = 0
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    t0 = time.perf_counter_ns()
    om = omega_solve(n, max_harmonics=200)
    total_time += time.perf_counter_ns() - t0
    count += 1

avg_us = total_time / count / 1000
print(f"Average: {avg_us:.1f} us per n (was 6.6 us original, 243 us unoptimized)")
print(f"Total: {total_time/1e9:.3f}s for {count} values")

# Scale test
print("\n=== Scale test ===")
for limit in [100000, 500000, 1000000]:
    t0 = time.perf_counter()
    sq_count = 0
    om_count = 0
    for k_val in range(1, limit // 24 + 1):
        n = 24 * k_val + 1
        if n > limit: break
        sq = False
        # quick squareful check
        m = n
        p = 2
        while p * p <= m:
            if m % p == 0:
                c = 0
                while m % p == 0:
                    m //= p
                    c += 1
                if c == 1:
                    break
            p += 1 if p == 2 else 2
        else:
            if m == 1:
                sq = True
        if sq:
            sq_count += 1
            om = omega_solve(n, max_harmonics=200)
            if om:
                om_count += 1
    t = time.perf_counter() - t0
    print(f"n <= {limit:>7d}: {sq_count:>4d} squareful, Omega solves {om_count:>4d}/{sq_count:>4d}, time={t:.1f}s")
