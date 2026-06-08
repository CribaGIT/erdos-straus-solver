"""Test p=193 (p ≡ 1 mod 24, c = (p+3)/4 = 49, all divisors of c² ≡ 1 mod 3).
Prediction: 4c-p=3 formula fails; Omega uses different A (like 4c-p=7 as with p=73).
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_solve, omega_divisors

p = 193
n = p * p
print(f"n = p² = {p}² = {n}")
print(f"n mod 24 = {n % 24} (should be 1)")
print(f"p mod 4 = {p % 4}")
print()

# Expected c for 4c-p = 3
c3 = (p + 3) // 4
print(f"For 4c-p = 3: c = (p+3)/4 = {c3}")
print(f"  c mod 3 = {c3 % 3}")
print(f"  Divisors of c² = {c3**2}: {omega_divisors(c3**2)}")
print(f"  Any divisor == 2 mod 3? {any(d % 3 == 2 for d in omega_divisors(c3**2))}")
print()

# Try 4c-p = 3: A = 3p
A3 = 3 * p
c3_val = (p + 3) // 4
x3 = c3_val * p
nx3 = n * x3
target_mod3 = (-nx3) % A3
print(f"4c-p = 3: A={A3}, x={x3}")
print(f"  target_mod = (-nx) % A = {target_mod3}")
# Check all divisors of c3²
c3_sq = c3_val * c3_val
for d_candidate in omega_divisors(c3_sq):
    d = d_candidate * p  # k * p
    if d % A3 == target_mod3:
        y3 = (nx3 + d) // A3
        z3 = (nx3 + nx3 * nx3 // d) // A3
        if y3 > 0 and z3 > 0 and 4 * x3 * y3 * z3 == n * (x3*y3 + x3*z3 + y3*z3):
            print(f"  FOUND: d={d}, y={y3}, z={z3}")
            break
else:
    print(f"  NOT FOUND — as predicted")
print()

# Now try Omega solver
print(f"Omega solver result (h=200):")
om = omega_solve(n, max_harmonics=200)
if om:
    A = om['A']
    c = (om['x'] // p)  # x = c*p
    print(f"  A={A}, x={om['x']}, y={om['y']}, z={om['z']}")
    print(f"  A/p = {A // p}")
    print(f"  c = x/p = {c}")
    print(f"  4c-p = {4*c - p}")
    
    # Also check the 4c-p=3 case (even if it failed, show A=3p and which divisor would work)
    print(f"\n  For comparison, 4c-p=3 would give A=3p={3*p}, c={c3}")
    print(f"  Actual used: A={A}, c={c}")
    print(f"  So 4c-p = {4*c-p} was needed (not 3)")
else:
    print("  NOT FOUND — would be a counterexample!")
