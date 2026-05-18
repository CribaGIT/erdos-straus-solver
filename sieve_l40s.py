import numpy as np, json, time, hashlib, os, sys
from datetime import datetime

print('=' * 50)
print('ERDOS-STRAUS SIEVE — Lightning L40S Worker')
print(f'Start: {datetime.now().isoformat()}')
print('GPU: L40S — 48GB VRAM')
print('=' * 50)

try:
    import cupy as cp
    gpu = True
    print(f'CuPy available: {cp.cuda.runtime.getDeviceCount()} GPU(s)')
except:
    gpu = False
    print('CuPy not available — falling back to NumPy CPU')
    import numpy as cp

CHUNK_SIZE = 10_000_000
MAX_TIME = 4 * 3600
start_time = time.time()

solutions = []
stable_count = 0
breach_count = 0

def erdos_straus_check(n):
    found = 0
    stable = False
    max_denom = int(n * n * 0.5)
    for x in range(int(n/4) + 1, min(int(3*n/4), max_denom)):
        x4 = 4 * x - n
        if x4 <= 0: continue
        for y in range(x, min(int(2*n*x/x4), max_denom)):
            y4 = x4 * y - n * x
            if y4 <= 0: continue
            if (n * x * y) % y4 == 0:
                z = (n * x * y) // y4
                if z >= y:
                    found += 1
                    if found >= 100:
                        stable = True
                        return found, stable
    return found, stable

n_start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
n_end = int(sys.argv[2]) if len(sys.argv) > 2 else n_start + CHUNK_SIZE

print(f'Search: {n_start:,} to {n_end:,}')

for n in range(n_start, n_end):
    if time.time() - start_time > MAX_TIME:
        print(f'Time limit at n={n}')
        break
    count, stable = erdos_straus_check(n)
    if count > 0:
        solutions.append(dict(n=int(n), solutions=count,
            classification='STABLE' if stable else 'BREACH',
            timestamp=datetime.now().isoformat()))
        if stable: stable_count += 1
        else: breach_count += 1
    if n % 100000 == 0:
        elapsed = time.time() - start_time
        rate = (n - n_start) / elapsed if elapsed > 0 else 0
        print(f'  n={n:,} | {stable_count} STABLE | {breach_count} BREACH | {rate:.0f}/s | {elapsed/3600:.1f}h')

output = dict(source='lightning_l40s', start_n=n_start, last_n=n_end,
    solutions_found=len(solutions), stable=stable_count, breach=breach_count,
    runtime_seconds=time.time()-start_time, solutions=solutions[:100],
    timestamp=datetime.now().isoformat())

with open('/tmp/erdos_l40s_output.json','w') as f:
    json.dump(output, f, indent=2)
print(f'Saved. {stable_count} STABLE, {breach_count} BREACH')