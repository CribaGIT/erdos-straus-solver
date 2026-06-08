"""Test if the 3 unsolved n values are solvable with deeper search."""
import sys
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

unsolved = [5329, 7921, 9409]
for n in unsolved:
    print(f'n={n}:')
    # Omega — try deeper
    found = None
    for h in [50, 100, 200, 500, 1000, 2000, 5000, 10000]:
        om = omega_solve(n, max_harmonics=h)
        if om:
            found = om
            print(f'  Omega (h={h}): x={om["x"]}, y={om["y"]}, z={om["z"]}, A={om["A"]}, d={om["d"]}')
            break
    if not found:
        print(f'  Omega: not found up to h=10000')

    # Bradford — try deeper
    found = None
    for k in [50, 100, 200, 500, 1000]:
        b1 = bradford_type1_solve(n, max_k=k)
        b2 = bradford_type2_solve(n, max_k=k)
        br = b1 or b2
        if br:
            found = br
            print(f'  Bradford (k={k}): x={br["x"]}, y={br["y"]}, z={br["z"]}, method={br["method"]}')
            break
    if not found:
        print(f'  Bradford: not found up to k=1000')
    print()
