#!/usr/bin/env python
"""ERDOS SIEVE — Lightning A100 Worker"""
import numpy as np, json, time, os, sys
from datetime import datetime

print('=' * 50)
print('ERDOS-STRAUS SIEVE — Lightning A100 Worker')
print(f'Start: {datetime.now().isoformat()}')
print('GPU: A100 — 40GB VRAM')
print('=' * 50)

try:
    import cupy as cp
    GPU = True
    print(f'CuPy on A100: {cp.cuda.runtime.getDeviceCount()} GPU(s)')
except:
    GPU = False
    cp = np
    print('CuPy unavailable — using NumPy CPU')

CHUNK = 10_000_000
MAX_TIME = 3.0 * 3600
start = time.time()

n_start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
n_end   = int(sys.argv[2]) if len(sys.argv) > 2 else n_start + CHUNK

print(f'Range: {n_start:,} -> {n_end:,} ({n_end-n_start:,} integers)')
print(f'Time limit: {MAX_TIME/3600:.1f}h')
print()

BATCH = 50000
solutions = []
stable_count = 0
breach_count = 0

def sieve_batch(n_vals):
    results = []
    for n in n_vals:
        n4 = 4.0 / n
        x_min = int(n/4) + 1
        x_max = min(int(3*n/4), int(n*n*0.3))
        
        if x_max <= x_min:
            results.append({'n': int(n), 'solutions': 0, 'classification': 'VOID',
                           'mod9': n % 9, 'ts': datetime.now().isoformat()})
            continue
        
        found = 0
        mod9 = n % 9
        probe_limit = 200 if mod9 in (0, 3, 6) else 800
        
        for x in range(x_min, min(x_min + probe_limit, x_max)):
            x4 = 4*x - n
            if x4 <= 0:
                continue
            if (n*x) % x4 != 0:
                continue
            
            z = (n*x) // x4
            y_lim = min(int(2*n*x/x4) + 1, int(n*n*0.3))
            
            for y in range(x, y_lim):
                denom = x4*y - n*x
                if denom <= 0:
                    continue
                if (n*x*y) % denom == 0:
                    found += 1
                    if found >= 3:
                        break
            if found >= 3:
                break
        
        if found > 0:
            classification = 'STABLE' if found >= 3 else 'BREACH'
            results.append({
                'n': int(n), 'solutions': found,
                'classification': classification,
                'mod9': mod9,
                'ts': datetime.now().isoformat()
            })
    
    return results


batch_n = []
last_n = n_start

for n in range(n_start, n_end):
    if time.time() - start > MAX_TIME:
        print(f'\nTime limit reached at n={n:,}')
        last_n = n
        break
    
    batch_n.append(n)
    last_n = n
    
    if len(batch_n) >= BATCH or n == n_end - 1:
        batch_results = sieve_batch(batch_n)
        for r in batch_results:
            solutions.append(r)
            if r['classification'] == 'STABLE':
                stable_count += 1
            elif r['classification'] == 'BREACH':
                breach_count += 1
        
        elapsed = time.time() - start
        rate = (n - n_start) / elapsed if elapsed > 0 else 0
        progress = (last_n - n_start) / (n_end - n_start) * 100
        print(f'  n={n:>12,}  |  STABLE:{stable_count:>5}  BREACH:{breach_count:>5}  '
              f'rate={rate:>8.0f}/s  |  {elapsed/3600:.1f}h/{MAX_TIME/3600:.1f}h  |  {progress:.1f}%')
        batch_n = []

# Output survives in the terminal log AND as a file
# Download: Files sidebar → right-click erdos_a100_output.json → Download
print(f'\n=== A100 RUN COMPLETE ===')
print(f'Range: {n_start:,} -> {last_n:,}')
print(f'STABLE: {stable_count}  |  BREACH: {breach_count}')
print(f'Runtime: {(time.time()-start)/3600:.2f}h')
print(f'Vinculum: ({stable_count}+{breach_count})/{last_n-n_start} classified')

# Full output to file
output = {
    'source': 'lightning_a100', 'start_n': n_start, 'last_n': last_n,
    'solutions_found': len(solutions), 'stable': stable_count, 'breach': breach_count,
    'runtime_seconds': time.time() - start, 'solutions': solutions,
    'timestamp': datetime.now().isoformat()
}
with open('erdos_a100_output.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f'File: erdos_a100_output.json (download from Files sidebar)')

# Compact copy-paste backup
print('\n=== OUTPUT (COPY THIS AS BACKUP) ===')
print(json.dumps({'s':stable_count,'b':breach_count,'n_start':n_start,'n_end':last_n,
    'runtime_h':round((time.time()-start)/3600,2)}))
