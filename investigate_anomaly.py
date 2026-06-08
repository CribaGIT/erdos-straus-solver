"""Check if Omega's d|x constraint is too restrictive.
The condition should be d | nx (or d | nx²), not d | x.
For n=2521, the Bradford solution has d=1304, x=652, nx=1643692.
Check: d|x? d|nx? d|nx²?
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_divisors

n = 2521
br_x, br_y, br_z = 652, 18908, 23833534
A = 4 * br_x - n  # should be 87
nx = n * br_x

print(f"n={n}, x={br_x}, A={A}, nx={nx}")
print(f"A mod 4 = {A % 4} (should be 3)")

d = br_y * A - nx
print(f"d = y*A - nx = {br_y}*{A} - {nx} = {d}")

print(f"d | x? {br_x % d == 0} (x % d = {br_x % d})")
print(f"d | nx? {nx % d == 0} (nx % d = {nx % d})")
print(f"d | nx²? {(nx*nx) % d == 0}")

# What divides nx?
nx_divs = omega_divisors(nx)
print(f"\nNumber of divisors of nx = {len(nx_divs)}")
print(f"d in nx_divs? {d in nx_divs}")

# Now check: does d divide nx²?
nx2_divs = omega_divisors(nx * nx)
print(f"Number of divisors of nx² = {len(nx2_divs)}")
print(f"d in nx2_divs? {d in nx2_divs}")

# What's the correct constraint? d must divide nx² for integer z
# And also A | (nx + d) for integer y
# And A | (nx + nx²/d) for integer z
print(f"\nA | (nx + d)? {(nx + d) % A == 0}")
nx2_over_d = (nx * nx) // d if (nx * nx) % d == 0 else None
print(f"nx² / d = {nx2_over_d} (integer: {nx2_over_d is not None})")
if nx2_over_d is not None:
    print(f"A | (nx + nx²/d)? {(nx + nx2_over_d) % A == 0}")
    z_from_omega = (nx + nx2_over_d) // A
    print(f"z from Omega formula = {z_from_omega} (expected {br_z})")

# Now check the brute-force solution (636, 69748, 131876031)
print("\n" + "=" * 80)
print("Brute-force solution analysis")
print("=" * 80)
x2, y2, z2 = 636, 69748, 131876031
A2 = 4 * x2 - n
d2 = y2 * A2 - n * x2
nx2 = n * x2
print(f"x={x2}, A={A2}, d={d2}")
print(f"A mod 4 = {A2 % 4}")
print(f"d | x? {x2 % d2 == 0}")
print(f"d | nx? {nx2 % d2 == 0}")
print(f"d | nx²? {(nx2*nx2) % d2 == 0}")
print(f"A | (nx+d)? {(nx2 + d2) % A2 == 0}")

# Now check all brute-force solutions
print("\n" + "=" * 80)
print("Check all brute-force solutions against Omega formula")
print("=" * 80)

# Re-run brute force with extended range
solutions_set = set()
x_lo = n // 4 + 1
x_hi = 3 * n // 4
for x in range(x_lo, x_hi + 1):
    D = 4 * x - n
    if D <= 0: continue
    nx_val = n * x
    y_lo = nx_val // D + 1
    for y in range(y_lo, min(y_lo + 50000, nx_val * 2)):
        num = n * x * y
        den = y * D - nx_val
        if den <= 0: break
        if num % den != 0: continue
        z = num // den
        if z < y: continue
        if 4 * x * y * z == n * (x*y + x*z + y*z):
            solutions_set.add(tuple(sorted((x,y,z))))
            if len(solutions_set) >= 20:
                break
    if len(solutions_set) >= 20:
        break

print(f"Found {len(solutions_set)} solutions")
for sx, sy, sz in sorted(solutions_set)[:10]:
    A_val = 4 * sx - n
    d_val = sy * A_val - n * sx
    nx_val = n * sx
    d_divides_x = (sx % d_val == 0)
    d_divides_nx = (nx_val % d_val == 0)
    d_divides_nx2 = ((nx_val * nx_val) % d_val == 0)
    print(f"  x={sx:4d}, A={A_val:3d}, d={d_val:7d}: d|x={d_divides_x}, d|nx={d_divides_nx}, d|nx²={d_divides_nx2}")

print("\n✓ d|x is too restrictive — should be d|nx²")
print("  Fixed Omega solver would check divisors of nx (cheaper) or nx²")
