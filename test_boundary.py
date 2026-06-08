"""Find the exact boundary of Bradford's failure domain.
Hypothesis: Bradford fails on n = p^k (single prime power, k>=2).
Testing: n = p^3, p^4, p*q*r, p^2*q^2, etc.
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

def test_n(n, h=200, k=500):
    om = omega_solve(n, max_harmonics=h)
    br = bradford_type1_solve(n, max_k=k) or bradford_type2_solve(n, max_k=k)
    return {
        "n": n, "omega": om is not None, "bradford": br is not None,
        "om": om, "br": br,
    }

print("=" * 80)
print("BRADFORD FAILURE BOUNDARY: prime powers")
print("=" * 80)
# n = p^3 where p = 1 mod 24
for p in [73, 97, 193, 241]:
    n = p**3
    if n <= 200000:
        r = test_n(n)
        print(f"  n={p}^3 = {n}: Omega={r['omega']}, Bradford={r['bradford']}")
        if r['omega']:
            print(f"    Omega: ({r['om']['x']}, {r['om']['y']}, {r['om']['z']})")
print()

# n = p^4
for p in [73, 97]:
    n = p**4
    if n <= 200000:
        r = test_n(n)
        print(f"  n={p}^4 = {n}: Omega={r['omega']}, Bradford={r['bradford']}")
print()

print("=" * 80)
print("BRADFORD FAILURE BOUNDARY: higher powers")
print("=" * 80)
# n = p^2 * q^2
for p, q in [(5, 73), (7, 73), (11, 97)]:
    n = p**2 * q**2
    if n <= 200000 and n % 4 == 1:
        r = test_n(n)
        print(f"  n={p}^2*{q}^2 = {n}: Omega={r['omega']}, Bradford={r['bradford']}")
print()

# n = p * q * r
for p, q, r in [(5, 13, 73), (7, 13, 97), (5, 17, 73)]:
    n = p * q * r
    if n % 4 == 1:
        r = test_n(n)
        print(f"  n={p}*{q}*{r} = {n}: Omega={r['omega']}, Bradford={r['bradford']}")
        if r['omega'] and r['bradford']:
            om_s = tuple(sorted((r['om']['x'], r['om']['y'], r['om']['z'])))
            br_s = tuple(sorted((r['br']['x'], r['br']['y'], r['br']['z'])))
            print(f"    Disjoint: {om_s != br_s}")
print()

print("=" * 80)
print("SYSTEMATIC: all n=1 mod 24 up to 5000")
print("  Identify which n are Omega-only and analyze their factorization")
print("=" * 80)

omega_only_n = []
for k in range(1, 5000//24 + 1):
    n = 24 * k + 1
    if n > 5000: break
    r = test_n(n, h=200, k=500)
    if r['omega'] and not r['bradford']:
        # Analyze factorization
        def prime_factors(m):
            factors = []
            d = 2
            while d * d <= m:
                while m % d == 0:
                    factors.append(d)
                    m //= d
                d += 1
            if m > 1:
                factors.append(m)
            return factors
        factors = prime_factors(n)
        from collections import Counter
        fcount = Counter(factors)
        powers = list(fcount.values())
        is_prime_power = len(set(factors)) == 1
        max_power = max(powers)
        omega_only_n.append({
            "n": n,
            "factors": factors,
            "is_prime_power": is_prime_power,
            "max_power": max_power,
            "signature": sorted(powers),
        })

print(f"  Omega-only count (n<=5000): {len(omega_only_n)}")
print()

# Group by factorization signature
from collections import defaultdict
by_sig = defaultdict(list)
for entry in omega_only_n:
    key = tuple(entry["signature"])
    by_sig[key].append(entry)

print("  By factorization signature:")
for sig, entries in sorted(by_sig.items()):
    print(f"    powers={list(sig)}: {len(entries)} cases")
    if len(entries) <= 5:
        for e in entries:
            print(f"      n={e['n']} = {'*'.join(str(f) for f in e['factors'])}")

print()
print("  CONCLUSION: identify the exact condition for Bradford failure")
