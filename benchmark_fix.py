"""Performance comparison: old vs fixed Omega solver."""
import sys, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve

# Test on all n=1 mod 24 up to 10000
import math

print("=== Performance benchmark: fixed Omega solver ===")
total_time = 0
count = 0
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    t0 = time.perf_counter_ns()
    om = omega_solve(n, max_harmonics=200)
    t = time.perf_counter_ns() - t0
    total_time += t
    count += 1

avg_us = total_time / count / 1000
print(f"  Average: {avg_us:.1f} us per n (was 6.6 us)")
print(f"  Total: {total_time/1e9:.3f}s for {count} values")

# Also check worst-case (n with most divisors)
print()
print("=== Worst-case n (most divisors) ===")
max_time = 0
max_n = 0
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    t0 = time.perf_counter_ns()
    om = omega_solve(n, max_harmonics=200)
    t = time.perf_counter_ns() - t0
    if t > max_time:
        max_time = t
        max_n = n

print(f"  Slowest: n={max_n} at {max_time/1000:.1f} us ({max_time/1e9:.6f}s)")
