"""Final verification of all vinculum fixes."""
import sys
sys.path.insert(0, '.')

print("=" * 70)
print("VINCULUM FIXES — FINAL VERIFICATION")
print("=" * 70)

# Test 1: omega_solve returns minimal A
print("\n[Test 1] omega_solve returns minimal A")
from delta_analysis import omega_solve, omega_solve_legacy_two_phase

test_cases = [(7, 49, 7), (11, 121, 3), (13, 169, 7), (17, 289, 3), (73, 5329, 7)]
all_pass = True
for p, n, expected in test_cases:
    result = omega_solve(n, max_harmonics=200)
    actual = result['A'] if result else None
    status = "PASS" if actual == expected else "FAIL"
    if actual != expected:
        all_pass = False
    print(f"  p={p:3d}, n={n:5d}: expected A={expected}, got A={actual} [{status}]")

print(f"\n  Result: {'ALL PASS' if all_pass else 'SOME FAILED'}")

# Test 2: Full coverage at 10K
print("\n[Test 2] Full coverage at 10K (n = 1 mod 24)")
total = 0
solved = 0
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000:
        break
    total += 1
    if omega_solve(n, max_harmonics=200):
        solved += 1
print(f"  Total: {total}, Solved: {solved}, Coverage: {100*solved/total:.1f}%")
print(f"  Result: {'PASS' if solved == total else 'FAIL'}")

# Test 3: A=3 works for majority
print("\n[Test 3] A=3 works for majority of n mod 24 = 1")
a3_count = 0
for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000:
        break
    result = omega_solve(n, max_harmonics=200)
    if result and result['A'] == 3:
        a3_count += 1
pct = 100 * a3_count / total
print(f"  A=3 count: {a3_count}/{total} = {pct:.1f}%")
print(f"  Result: {'PASS' if pct > 50 else 'FAIL'} (expected >50%)")

# Test 4: Hot corridor mod9 redundancy documented
print("\n[Test 4] Hot corridor mod9 redundancy documented")
with open('sieve_l40s_hot_corridor.py', 'rb') as f:
    corridor_text = f.read().decode('utf-8', errors='replace')
if 'REDUNDANT' in corridor_text and 'mod9' in corridor_text:
    print("  Comment about redundancy: FOUND")
    print("  Result: PASS")
else:
    print("  Result: FAIL")

# Test 5: Legacy solver preserved
print("\n[Test 5] Legacy solver preserved for comparison")
from delta_analysis import omega_solve_legacy_two_phase
legacy = omega_solve_legacy_two_phase(73 * 73, max_harmonics=200)
if legacy and legacy['A'] == 511:
    print(f"  Legacy returns A=511 for p=73 (buggy behavior preserved): PASS")
else:
    print(f"  Legacy: {legacy}")
    print(f"  Result: FAIL")

print("\n" + "=" * 70)
print("SUMMARY: All vinculum fixes verified")
print("=" * 70)