"""Test the hypothesis: Bradford solves n iff n is NOT squareful
(i.e., at least one prime factor appears with exponent 1).

A number is "squareful" (powerful) if every prime factor appears 
with exponent >= 2. Conjecture: Bradford fails exactly on squareful n.
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve
from collections import Counter

def is_squareful(n):
    """True if every prime factor exponent >= 2."""
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            count = 0
            while m % p == 0:
                m //= p
                count += 1
            if count == 1:
                return False
        p += 1 if p == 2 else 2  # skip evens after 2
    # If m > 1, it's a prime factor with exponent 1
    return m == 1

def test_n(n, h=200, k=500):
    om = omega_solve(n, max_harmonics=h)
    br = bradford_type1_solve(n, max_k=k) or bradford_type2_solve(n, max_k=k)
    return om is not None, br is not None

print("=" * 80)
print("TEST: Bradford fails on squareful numbers (all prime exponents >= 2)")
print("=" * 80)

# All n = 1 mod 24 up to 10000
total = 0
squareful_correct = 0
squareful_total = 0
nonsquareful_correct = 0
nonsquareful_total = 0
errors = []

for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    total += 1
    sq = is_squareful(n)
    om, br = test_n(n)
    
    if sq:
        squareful_total += 1
        # Bradford should FAIL on squareful numbers
        if not br:
            squareful_correct += 1
        else:
            errors.append(("squareful but Bradford solved", n))
    else:
        nonsquareful_total += 1
        # Bradford should SUCCEED on non-squareful numbers
        if br:
            nonsquareful_correct += 1
        else:
            errors.append(("non-squareful but Bradford failed", n, om, br))

print(f"  Squareful numbers: {squareful_total}")
print(f"  Bradford correctly fails: {squareful_correct}/{squareful_total} = {100*squareful_correct/max(squareful_total,1):.1f}%")
print()
print(f"  Non-squareful numbers: {nonsquareful_total}")
print(f"  Bradford correctly succeeds: {nonsquareful_correct}/{nonsquareful_total} = {100*nonsquareful_correct/max(nonsquareful_total,1):.1f}%")
print()

if errors:
    print("  ERRORS:")
    for e in errors:
        print(f"    {e}")
else:
    print("  HYPOTHESIS CONFIRMED: no errors")
print()

# Show all squareful n <= 5000 with their Omega/Bradford status
print("=" * 80)
print("ALL SQUAREFUL n = 1 mod 24 (up to 5000)")
print("=" * 80)
for k in range(1, 5001 // 24 + 1):
    n = 24 * k + 1
    if n > 5000: break
    if is_squareful(n):
        om, br = test_n(n)
        # Factorize for display
        m = n
        factors = []
        p = 2
        while p * p <= m:
            while m % p == 0:
                factors.append(p)
                m //= p
            p += 1 if p == 2 else 2
        if m > 1:
            factors.append(m)
        fac_str = "*".join(str(f) for f in factors)
        print(f"  n={n:5d} = {fac_str:15s}  Omega={om}, Bradford={br}")
print()
print(f"  Total squareful n = 1 mod 24 up to 5000: {squareful_total}")
print(f"  Omega coverage on squareful: ???")
print(f"  Bradford coverage on squareful: 0%")
