"""Extend squareful barrier test to n <= 10^6.
Strategy:
1. Fast pre-scan: classify all n as squareful or not
2. Test Bradford on all non-squareful n (fast)
3. Test Omega only on squareful n (slow but few)
"""
import sys, math, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

def is_squareful(n):
    """True if every prime exponent >= 2."""
    m = n
    for p in range(2, int(math.isqrt(m)) + 1):
        if m % p == 0:
            count = 0
            while m % p == 0:
                m //= p
                count += 1
            if count == 1:
                return False
    return m == 1

def class_test_inner(limit, h=200, k=500):
    """Test barrier up to limit. Returns summary."""
    start = time.perf_counter()
    
    # Phase 1: Classify and test Bradford
    bradford_fail = []  # non-squareful where Bradford fails
    squareful_n = []
    bradford_time = 0
    
    for k_val in range(1, limit // 24 + 1):
        n = 24 * k_val + 1
        if n > limit:
            break
        sq = is_squareful(n)
        if sq:
            squareful_n.append(n)
        else:
            t0 = time.perf_counter_ns()
            br = bradford_type1_solve(n, max_k=k) or bradford_type2_solve(n, max_k=k)
            bradford_time += time.perf_counter_ns() - t0
            if not br:
                bradford_fail.append(n)
    
    # Phase 2: Test Omega on squareful numbers
    omega_fail = []
    omega_time = 0
    for n in squareful_n:
        t0 = time.perf_counter_ns()
        om = omega_solve(n, max_harmonics=h)
        omega_time += time.perf_counter_ns() - t0
        if not om:
            omega_fail.append(n)
    
    elapsed = time.perf_counter() - start
    
    total = len(squareful_n) + (limit//24 - len(squareful_n))
    return {
        "limit": limit,
        "total": total,
        "squareful": len(squareful_n),
        "nonsquareful": total - len(squareful_n),
        "bradford_fail": len(bradford_fail),
        "omega_fail": len(omega_fail),
        "bradford_time_s": bradford_time / 1e9,
        "omega_time_s": omega_time / 1e9,
        "elapsed_s": elapsed,
        "bradford_fail_examples": bradford_fail[:5],
        "omega_fail_examples": omega_fail[:5],
    }

for limit in [10000, 50000, 100000, 500000, 1000000]:
    r = class_test_inner(limit, h=200, k=500)
    print(f"n <= {r['limit']:>7d}: total={r['total']:>5d}, "
          f"squareful={r['squareful']:>4d}, "
          f"Bradford fails on non-squareful={r['bradford_fail']:>3d}, "
          f"Omega fails on squareful={r['omega_fail']:>3d}, "
          f"time={r['elapsed_s']:.1f}s "
          f"(Bradford={r['bradford_time_s']:.1f}s, Omega={r['omega_time_s']:.1f}s)")
    if r['bradford_fail']:
        print(f"  Bradford fail examples: {r['bradford_fail_examples']}")
    if r['omega_fail']:
        print(f"  Omega fail examples: {r['omega_fail_examples']}")
