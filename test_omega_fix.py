"""Test fixed Omega solver on n=2521 and all n up to 10000."""
import sys, math, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve

n = 2521
print(f"=== Fixed Omega solver on n={n} ===")
for h in [100, 200, 500]:
    t0 = time.perf_counter_ns()
    om = omega_solve(n, max_harmonics=h)
    t = (time.perf_counter_ns() - t0) / 1e9
    if om:
        print(f"  SOLVED at h={h} ({t*1000:.1f}ms): A={om['A']}, x={om['x']}, d={om['d']}, y={om['y']}, z={om['z']}")
        # Verify d|x? d|nx? d|nx²?
        nx = n * om['x']
        print(f"    d|x={om['x'] % om['d'] == 0}, d|nx={nx % om['d'] == 0}, d|nx²={(nx*nx) % om['d'] == 0}")
        break
    else:
        print(f"  NOT FOUND at h={h} ({t*1000:.1f}ms)")

print()
print(f"=== Re-run full analysis (h=200, k=500) ===")
from delta_analysis import bradford_type1_solve, bradford_type2_solve

both = 0
omega_only = 0
bradford_only = 0
neither = 0
anomalies_gone = True

for k in range(1, 10001 // 24 + 1):
    n = 24 * k + 1
    if n > 10000: break
    om = omega_solve(n, max_harmonics=200)
    br = bradford_type1_solve(n, max_k=500) or bradford_type2_solve(n, max_k=500)
    if om and br: both += 1
    elif om and not br: omega_only += 1
    elif br and not om: 
        bradford_only += 1
        anomalies_gone = False
        print(f"  REMAINING ANOMALY: n={n}")
    else: neither += 1

total = both + omega_only + bradford_only + neither
print(f"\nTotal: {total}, Both: {both}, Omega-only: {omega_only}, Bradford-only: {bradford_only}, Neither: {neither}")
print(f"Omega coverage: {100*(both+omega_only)/total:.1f}%")
print(f"Bradford coverage: {100*(both+bradford_only)/total:.1f}%")
print(f"All anomalies resolved: {anomalies_gone}")
