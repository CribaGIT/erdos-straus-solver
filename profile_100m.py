"""Quick profile test for factoring at large scale."""
import time, sys
sys.path.insert(0, '.')
from sweep_100m import *

print("Testing solver on exceptional primes near 10^8...")
t0 = time.perf_counter()
tested = 0
for p in range(99_999_989, 100_010_000, 12):
    if not is_p[p]:
        continue
    if not is_exceptional(p):
        continue
    info = find_min_A(p, max_m=200)
    m = (info["A"] - 3) // 4 if info else -1
    tested += 1
    elapsed = time.perf_counter() - t0
    rate = tested / elapsed if elapsed > 0 else 0
    print(f"  p={p}, A={info['A']}, m={m} ({rate:.1f}/s)")
    if tested >= 30:
        break
print(f"Total: {tested} primes in {time.perf_counter()-t0:.1f}s")
