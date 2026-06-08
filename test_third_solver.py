"""Third solver: comprehensive test on all n = 1 mod 24 up to 2000."""
import sys, math, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve, bradford_type1_solve, bradford_type2_solve

def brute_first_solve(n, y_search_limit=50000):
    """First (x,y,z) found with x ascending, then y ascending."""
    x_lo = n // 4 + 1
    x_hi = n * 10
    for x in range(x_lo, x_hi + 1):
        D = 4 * x - n
        if D <= 0:
            continue
        nx = n * x
        y_lo = max(x, nx // D + 1)
        for y in range(y_lo, y_lo + y_search_limit):
            num = n * x * y
            den = y * D - nx
            if den <= 0:
                break
            if num % den != 0:
                continue
            z = num // den
            if z < y:
                continue
            if 4 * x * y * z == n * (x*y + x*z + y*z):
                return {"x": x, "y": y, "z": z, "method": "BruteFirst"}
    return None

print("=" * 80)
print("THIRD SOLVER TEST: n = 1 mod 24 up to 2000")
print("=" * 80)

results = {"both": 0, "d_om": 0, "d_br": 0, "d_both": 0, "fail": 0}
for k in range(1, 2001 // 24 + 1):
    n = 24 * k + 1
    if n > 2000: break
    
    om = omega_solve(n, max_harmonics=200)
    br = bradford_type1_solve(n, max_k=500) or bradford_type2_solve(n, max_k=500)
    
    if not (om and br):
        continue
    
    t0 = time.perf_counter()
    bf = brute_first_solve(n, y_search_limit=50000)
    t = time.perf_counter() - t0
    if t > 0.1:
        print(f"  n={n} brute took {t:.2f}s")
    
    if not bf:
        results["fail"] += 1
        print(f"  n={n}: brute-force FAILED (search bound)")
        continue
    
    results["both"] += 1
    om_t = tuple(sorted((om['x'], om['y'], om['z'])))
    br_t = tuple(sorted((br['x'], br['y'], br['z'])))
    bf_t = tuple(sorted((bf['x'], bf['y'], bf['z'])))
    
    d_om = om_t != bf_t
    d_br = br_t != bf_t
    if d_om: results["d_om"] += 1
    if d_br: results["d_br"] += 1
    if d_om and d_br: results["d_both"] += 1
    
    if results["both"] <= 5:
        print(f"  n={n:4d}:")
        print(f"    Omega:    ({om['x']:5d}, {om['y']:8d}, {om['z']:12d})")
        print(f"    Bradford: ({br['x']:5d}, {br['y']:8d}, {br['z']:12d})")
        print(f"    BruteFirst: ({bf['x']:5d}, {bf['y']:8d}, {bf['z']:12d})")

total = results["both"]
print(f"\n=== Results ===")
print(f"  Total n tested (Omega+Bradford both solve): {total}")
print(f"  BruteFirst disjoint from Omega: {results['d_om']}/{total} = {100*results['d_om']/max(total,1):.1f}%")
print(f"  BruteFirst disjoint from Bradford: {results['d_br']}/{total} = {100*results['d_br']/max(total,1):.1f}%")
print(f"  BruteFirst disjoint from BOTH: {results['d_both']}/{total} = {100*results['d_both']/max(total,1):.1f}%")
print(f"  BruteFirst failed (search bound): {results['fail']}")
