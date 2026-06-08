"""Answer user questions about the Erdos-Straus vinculum analysis."""
import sys
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

# 1) What is A? Show A varies across solutions
print("=== What is A? ===")
print("A = 4m + 3 where m ranges 0..max_harmonics-1. It is a SEARCH PARAMETER,")
print("not a constant. Both solvers use it, but find different values leading to different (y,z).\n")

for n in [73, 97, 145, 217]:
    om = omega_solve(n, max_harmonics=50)
    br = bradford_type1_solve(n, max_k=50) or bradford_type2_solve(n, max_k=50)
    print(f'n={n}:')
    if om:
        m = (om["A"] - 3) // 4
        print(f'  Omega:   A={om["A"]} (m={m}), x={om["x"]}, y={om["y"]}, z={om["z"]}')
    if br:
        print(f'  Bradford: A={br["A"]}, method={br["method"]}, x={br["x"]}, y={br["y"]}, z={br["z"]}')
    # Show A difference
    if om and br:
        print(f'  A DIFFERENCE: |Omega_A - Bradford_A| = {abs(om["A"] - br["A"])}')
    print()

# 2) The 3 Omega-only cases
print("=== Omega-only at depth ===")
print("All 3 are n = p^2 (prime square). Bradford cannot solve composites.\n")
for n in [5329, 7921, 9409]:
    om = omega_solve(n, max_harmonics=200)
    br = bradford_type1_solve(n, max_k=1000) or bradford_type2_solve(n, max_k=1000)
    p = int(n ** 0.5)
    print(f'n={n} = {p}^2:')
    if om:
        m = (om["A"] - 3) // 4
        print(f'  Omega:   A={om["A"]} (m={m}), x={om["x"]}, y={om["y"]}, z={om["z"]}')
    print(f'  Bradford at k=1000: {"NOT FOUND" if not br else "SOLVED"}')
    print()

# 3) Canonicalization test: show sorted triples
print("=== Canonicalization test ===")
n_test = 73
om = omega_solve(n_test)
br = bradford_type1_solve(n_test, max_k=50) or bradford_type2_solve(n_test, max_k=50)
print(f'n={n_test}:')
print(f'  Omega raw:       ({om["x"]}, {om["y"]}, {om["z"]})')
print(f'  Bradford raw:    ({br["x"]}, {br["y"]}, {br["z"]})')
om_s = tuple(sorted((om["x"], om["y"], om["z"])))
br_s = tuple(sorted((br["x"], br["y"], br["z"])))
print(f'  Omega sorted:    {om_s}')
print(f'  Bradford sorted: {br_s}')
print(f'  Match after sort? {om_s == br_s}')
print()

# 4) Show 5 shared n with their (y,z) always different
print("=== Five shared n: same x, always different (y,z) ===")
shared = [73, 97, 145, 193, 217]
for n in shared:
    om = omega_solve(n)
    br = bradford_type1_solve(n) or bradford_type2_solve(n)
    same_yz = (om["y"] == br["y"] and om["z"] == br["z"])
    same_xyz = (om["x"] == br["x"] and om["y"] == br["y"] and om["z"] == br["z"])
    print(f'n={n}: same x={om["x"]==br["x"]}, same yz={same_yz}, same xyz={same_xyz}')
    print(f'  Omega y,z:   ({om["y"]}, {om["z"]})')
    print(f'  Bradford y,z: ({br["y"]}, {br["z"]})')
    print()
