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
    import numpy as cp
    GPU = False
    cp.asnumpy = lambda x: np.array(x) if not isinstance(x, np.ndarray) else x
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
    if not n_vals:
        return results

    # 1D Material Tensor Injection
    N = cp.array(n_vals, dtype=cp.int64)
    mod9 = N % 9
    
    # Identify probe limits based on Mod9 classification
    is_hot = (mod9 == 0) | (mod9 == 3) | (mod9 == 6)
    probe_limits = cp.where(is_hot, 200, 800)
    MAX_PROBE = int(cp.max(probe_limits))
    
    X_min = (N // 4) + 1
    X_max_limit = cp.minimum(3 * N // 4, cp.clip((N.astype(cp.float64)**2 * 0.3).astype(cp.int64), 0, 10_000_000_000))
    
    # Evaluate X domain in parallel (BATCH, MAX_PROBE)
    X_offset = cp.arange(MAX_PROBE, dtype=cp.int64)
    X = X_min[:, None] + X_offset[None, :]
    
    valid_X_mask = (X < X_max_limit[:, None]) & (X_offset[None, :] < probe_limits[:, None])
    
    X4 = 4 * X - N[:, None]
    valid_X_mask &= (X4 > 0)
    
    # Safe division mod check
    # Avoid div by zero in modulo by setting invalid X4 to 1
    safe_X4 = cp.where(valid_X_mask, X4, 1)
    NX = N[:, None] * X
    valid_X_mask &= ((NX % safe_X4) == 0)
    
    # For survived X tensors, we need to find Y
    # Extract the surviving (N_index, X_val) pairs
    N_indices, X_offsets = cp.nonzero(valid_X_mask)
    
    # We will track solutions per N
    found_counts = cp.zeros(len(N), dtype=cp.int32)
    
    # To avoid memory explosions on Y, we process the survived X sequentially or grouped
    # Since the number of valid X is small, we can fallback to Python loop for the Y domain 
    # OR vectorize Y. We'll do a bounded Y search for the valid pairs.
    
    # Move to CPU for the sparse Y search (much faster than looping in CuPy scalar)
    N_idx_cpu = cp.asnumpy(N_indices)
    X_off_cpu = cp.asnumpy(X_offsets)
    
    # Precompute host arrays for fast access
    N_host = cp.asnumpy(N)
    mod9_host = cp.asnumpy(mod9)
    X_min_host = cp.asnumpy(X_min)
    
    for i in range(len(N_idx_cpu)):
        idx = N_idx_cpu[i]
        if found_counts[idx] >= 3:
            continue # already STABLE
            
        n = int(N_host[idx])
        x = int(X_min_host[idx] + X_off_cpu[i])
        
        x4 = 4 * x - n
        if x4 <= 0: continue
        
        z_approx = (n * x) // x4
        y_lim = min(int(2 * n * x / x4) + 1, int(n * n * 0.3))
        
        y_start = max(x, (n * x) // x4 + 1)
        # Y domain search
        for y in range(y_start, y_lim):
            denom = x4 * y - n * x
            if denom <= 0: continue
            if (n * x * y) % denom == 0:
                found_counts[idx] += 1
                if found_counts[idx] >= 3:
                    break
                    
    found_host = cp.asnumpy(found_counts)
    
    ts = datetime.now().isoformat()
    for i in range(len(N_host)):
        f_cnt = int(found_host[i])
        m9 = int(mod9_host[i])
        if f_cnt > 0:
            classification = 'STABLE' if f_cnt >= 3 else 'BREACH'
            results.append({
                'n': int(N_host[i]), 'solutions': f_cnt,
                'classification': classification,
                'mod9': m9,
                'ts': ts
            })
        elif X_max_limit[i] <= X_min_host[i]:
            results.append({
                'n': int(N_host[i]), 'solutions': 0,
                'classification': 'VOID',
                'mod9': m9, 'ts': ts
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
