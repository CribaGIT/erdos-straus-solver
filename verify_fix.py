"""Verify omega_solve fix returns minimal A."""
import sys
sys.path.insert(0, '.')
from delta_analysis import omega_solve, omega_solve_legacy_two_phase

# Test cases: p, expected minimal A
test_cases = [
    (5, 25, 15),    # p=5, n=25
    (7, 49, 7),     # p=7, n=49
    (11, 121, 11),  # p=11, n=121
    (13, 169, 39),  # p=13, n=169
    (17, 289, 51),  # p=17, n=289
    (19, 361, 19),  # p=19, n=361
    (23, 529, 23),  # p=23, n=529
    (73, 5329, 7),  # p=73: BUGGY returns 511, FIXED returns 7
]

print("=" * 70)
print("VERIFICATION: omega_solve fix")
print("=" * 70)
print()

all_pass = True
for p, n, expected_A in test_cases:
    # Fixed solver
    result = omega_solve(n, max_harmonics=200)
    fixed_A = result['A'] if result else None

    # Legacy buggy solver
    legacy = omega_solve_legacy_two_phase(n, max_harmonics=200)
    legacy_A = legacy['A'] if legacy else None

    status = "PASS" if fixed_A == expected_A else "FAIL"
    if fixed_A != expected_A:
        all_pass = False

    print(f"p={p:3d}, n={n:5d}:")
    print(f"  Expected minimal A: {expected_A}")
    print(f"  Fixed solver:       A={fixed_A}  [{status}]")
    print(f"  Legacy buggy:       A={legacy_A}  {'(BUG)' if legacy_A != expected_A else ''}")
    print()

# Full coverage test
print("=" * 70)
print("FULL COVERAGE TEST (n = 1 mod 24, <= 10000)")
print("=" * 70)

total = 0
solved = 0
min_A_dist = {}

for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000:
        break
    total += 1
    result = omega_solve(n, max_harmonics=200)
    if result:
        solved += 1
        A = result['A']
        min_A_dist[A] = min_A_dist.get(A, 0) + 1

print(f"Total: {total}, Solved: {solved}, Coverage: {100*solved/total:.1f}%")
print()
print("Minimal A distribution (with FIXED solver):")
for A in sorted(min_A_dist):
    m = (A - 3) // 4
    pct = 100 * min_A_dist[A] / total
    print(f"  A={A:3d} (m={m:2d}): {min_A_dist[A]:4d} ({pct:.1f}%)")

print()
if all_pass:
    print("ALL TESTS PASS: omega_solve returns minimal A")
else:
    print("SOME TESTS FAILED")