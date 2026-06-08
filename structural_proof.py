"""Collect Omega solutions for n = p^2 (prime squared) cases.
Goal: find a pattern that generalizes to all squareful n.
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_solve

print("=" * 80)
print("OMEGA SOLUTIONS FOR n = p^2 (p prime, p = 1 mod 24)")
print("=" * 80)

for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
    n = p * p
    if n % 24 != 1:
        continue
    om = omega_solve(n, max_harmonics=200)
    if om:
        A = om['A']
        x = om['x']
        y = om['y']
        z = om['z']
        d = om['d']
        # Verify algebra
        # x = (n+A)/4
        # nx = n*x
        # d should divide nx²
        nx = n * x
        d_div_nx2 = (nx * nx) % d == 0
        
        # Express A in terms of p
        # A = 4m + 3, so m = (A-3)/4
        m = (A - 3) // 4
        
        # x = (p² + A) / 4
        
        print(f"  p={p:2d}: n={n:5d}: A={A:4d} (m={m:3d}), x={x:5d}, d={d:8d}")
        print(f"         y={y:12d}, z={z:16d}")
        print(f"         d|nx²={d_div_nx2}")
        print(f"         x = (p²+A)/4 = ({n}+{A})/4 = {(n+A)//4}")
        print(f"         d = yA - nx = {y}*{A} - {n}*{x} = {y*A - n*x}")
        print()
    else:
        print(f"  p={p:2d}: n={n:5d}: NOT FOUND at h=200")
        print()
