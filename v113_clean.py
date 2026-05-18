# ERDOS–STRAUS V113 — Quantum Flank 31 (Clean Script)
# Paste into Kaggle notebook — ONE cell at a time
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════
# CELL 1: Setup
# ═══════════════════════════════════════
import numpy as np, json, time, hashlib, os, subprocess
from datetime import datetime

try:
    result = subprocess.run(['nvidia-smi','--query-gpu=name','--format=csv,noheader'],
                          capture_output=True, text=True, timeout=5)
    GPU = result.stdout.strip() if result.returncode == 0 else 'CPU'
except:
    GPU = 'CPU'

print(f'GPU: {GPU} | NumPy: {np.__version__}')

# ═══════════════════════════════════════
# CELL 2: Config
# ═══════════════════════════════════════
TARGET = 1_000_000_000
CHUNK = 1_000_000
MOD24 = [1, 5, 7, 9, 11, 13, 17, 19, 23]
print(f'Target: {TARGET:,} | Chunk: {CHUNK:,} | Mod24: {MOD24}')

# ═══════════════════════════════════════
# CELL 3: Sieve
# ═══════════════════════════════════════
def sieve(start, end, mod24_classes):
    sols = []
    n_vals = np.arange(start, end, dtype=np.int64)
    for mc in mod24_classes:
        cands = n_vals[n_vals % 24 == mc]
        for n in cands[:300]:
            xs = max(1, (n + 3) // 4)
            xe = n * 2
            step = max(1, (xe - xs) // 60)
            for x in range(xs, xe + 1, step):
                d = 4 * x - n
                if d <= 0:
                    continue
                ys = max(1, (n * x + d - 1) // d)
                ye = (2 * n * x // d) if d > 0 else (n * 2)
                if ye < ys:
                    continue
                for y in range(ys, min(ye + 1, ys + 30)):
                    dz = 4 * x * y - n * (x + y)
                    if dz > 0 and (n * x * y) % dz == 0:
                        z = (n * x * y) // dz
                        if z > 0:
                            sols.append({'n': int(n), 'x': int(x), 'y': int(y), 'z': int(z), 'm': mc})
                            break
                if sols:
                    break
    return sols

print('Sieve ready')

# ═══════════════════════════════════════
# CELL 4: Run
# ═══════════════════════════════════════
print('Running...')
chunks_done = 0
total_sols = 0
stable = 0
breach = 0

for cs in range(2, TARGET, CHUNK):
    ce = min(cs + CHUNK, TARGET)
    sols = sieve(cs, ce, MOD24)
    total_sols += len(sols)
    chunks_done += 1
    
    if sols:
        tors = [s['n'] * s['z'] / (s['x'] + s['y']) for s in sols if (s['x'] + s['y']) > 0]
        if tors and len(tors) > 1:
            sp = np.std(tors)
            if sp / (np.mean(tors) + 1) < 0.3:
                stable += 1
            else:
                breach += 1
    
    if chunks_done % 100 == 0:
        print(f'  [{ce/TARGET*100:.1f}%] {total_sols} solutions | STABLE:{stable} BREACH:{breach}')

print(f'\nDONE: {total_sols:,} solutions | STABLE:{stable} | BREACH:{breach}')

# ═══════════════════════════════════════
# CELL 5: Save
# ═══════════════════════════════════════
output = {
    'flank': 31,
    'version': 'v113',
    'gpu': GPU,
    'target': TARGET,
    'solutions': total_sols,
    'stable': stable,
    'breach': breach,
    'ts': datetime.now().isoformat(),
    'hash': hashlib.sha256(f'{total_sols}{stable}{breach}'.encode()).hexdigest()
}

with open('/kaggle/working/v113_output.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f'\nSaved to /kaggle/working/v113_output.json')
print(f'Hash: {output["hash"][:16]}...')
print(f'\nCOPY THIS FOR LOCAL MERGE:')
print(json.dumps(output))
