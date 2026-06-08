"""Test the disjoint factorization conjecture on new n families.
Tests:
1. n = p^2 * q (composite, not prime) — Bradford should fail
2. n = p * q (semiprime) — Bradford should fail
3. n = p^2 (prime square) — re-confirm Bradford fails
4. n = p (prime, n=1 mod 24) — both should succeed, with disjoint triples
"""
import sys
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve
import math

def test_n(n, label=""):
    om = omega_solve(n, max_harmonics=200)
    br = bradford_type1_solve(n, max_k=200) or bradford_type2_solve(n, max_k=200)
    result = {
        "n": n,
        "label": label,
        "omega": om is not None,
        "bradford": br is not None,
        "omega_triple": (om["x"], om["y"], om["z"]) if om else None,
        "bradford_triple": (br["x"], br["y"], br["z"]) if br else None,
        "disjoint": True,
    }
    if om and br:
        om_s = tuple(sorted((om["x"], om["y"], om["z"])))
        br_s = tuple(sorted((br["x"], br["y"], br["z"])))
        result["disjoint"] = (om_s != br_s)
    return result


print("=" * 80)
print("TEST: n = p^2 * q  (Bradford should fail — n is composite)")
print("=" * 80)
test_cases = [
    (5**2 * 73, "5^2 * 73"),
    (5**2 * 97, "5^2 * 97"),
    (7**2 * 73, "7^2 * 73"),
    (11**2 * 73, "11^2 * 73"),
    (13**2 * 97, "13^2 * 97"),
]
for n, label in test_cases:
    if n % 4 == 1:
        r = test_n(n, label)
        print(f"  {label} = {n}: Omega={r['omega']}, Bradford={r['bradford']}, Disjoint={r['disjoint']}")
        if r['omega']:
            print(f"    Omega triple: {r['omega_triple']}")
print()

print("=" * 80)
print("TEST: n = p * q  (semiprime, n=1 mod 4)")
print("=" * 80)
test_cases = [
    (5 * 73, "5*73"),
    (5 * 97, "5*97"),
    (13 * 73, "13*73"),
    (17 * 73, "17*73"),
    (29 * 73, "29*73"),
]
for n, label in test_cases:
    if n % 4 == 1:
        r = test_n(n, label)
        print(f"  {label} = {n}: Omega={r['omega']}, Bradford={r['bradford']}, Disjoint={r['disjoint']}")
        if r['omega'] and r['bradford']:
            print(f"    Omega: {r['omega_triple']}")
            print(f"    Bradford: {r['bradford_triple']}")
print()

print("=" * 80)
print("TEST: n = p (prime, n=1 mod 24) — reconfirm disjoint")
print("=" * 80)
test_cases = [73, 97, 193, 241, 313, 337, 409, 433]
for n in test_cases:
    r = test_n(n)
    if r['omega'] and r['bradford']:
        print(f"  n={n} (prime): Omega={r['omega']}, Bradford={r['bradford']}, Disjoint={r['disjoint']}")
        print(f"    Omega: {r['omega_triple']}")
        print(f"    Bradford: {r['bradford_triple']}")
print()

print("=" * 80)
print("TEST: n composite NOT of form p^2 — random samples")
print("=" * 80)
test_ns = [145, 265, 385, 481, 505, 649, 745, 793, 865]
for n in test_ns:
    r = test_n(n)
    if r['omega'] and r['bradford']:
        print(f"  n={n}: Omega={r['omega']}, Bradford={r['bradford']}, Disjoint={r['disjoint']}")
        print(f"    Omega: {r['omega_triple']}")
        print(f"    Bradford: {r['bradford_triple']}")
    elif r['omega'] and not r['bradford']:
        print(f"  n={n}: Omega only (Bradford fails)")
    elif not r['omega'] and r['bradford']:
        print(f"  n={n}: Bradford only (Omega fails)")
    else:
        print(f"  n={n}: neither (unexpected)")
print()

# Summary statistics
print("=" * 80)
print("AGGREGATE: Test all n=1 mod 24 up to 10000 for disjointness")
print("=" * 80)
total = 0
both = 0
disjoint = 0
omega_only = 0
bradford_only = 0
neither = 0
for k in range(1, 418):
    n = 24 * k + 1
    if n > 10000: break
    r = test_n(n)
    total += 1
    if r['omega'] and r['bradford']:
        both += 1
        if r['disjoint']:
            disjoint += 1
    elif r['omega'] and not r['bradford']:
        omega_only += 1
    elif r['bradford'] and not r['omega']:
        bradford_only += 1
    else:
        neither += 1

print(f"  Total n tested: {total}")
print(f"  Both solvers succeed: {both}")
print(f"  Disjoint triples: {disjoint}/{both} = {100*disjoint/max(both,1):.1f}%")
print(f"  Omega only: {omega_only}")
print(f"  Bradford only: {bradford_only}")
print(f"  Neither: {neither}")
print()
print(f"  CONJECTURE STATUS: {'CONFIRMED' if disjoint == both and neither == 0 else 'DISPROVEN'}")
