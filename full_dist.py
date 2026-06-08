"""Find actual minimal A for all exceptional primes up to 200000."""
import math, sys, time

def factorize(n):
    m = n
    res = {}
    q = 2
    while q * q <= m:
        while m % q == 0:
            res[q] = res.get(q, 0) + 1
            m //= q
        q += 1 if q == 2 else 2
    if m > 1:
        res[m] = res.get(m, 0) + 1
    return res

def divisors_from_factors(factors):
    divs = [1]
    for prime, exp in factors.items():
        cur = []
        p_pow = 1
        for _ in range(exp + 1):
            for d in divs:
                cur.append(d * p_pow)
            p_pow *= prime
        divs = cur
    return divs

def check_A(p, A):
    n = p * p
    if (n + A) % 4 != 0:
        return False, None
    x = (n + A) // 4
    nx = n * x
    target_mod = (-nx) % A
    fac = factorize(x)
    for q in list(fac):
        fac[q] *= 2
    fac[p] = fac.get(p, 0) + 4
    divs = divisors_from_factors(fac)
    for d in divs:
        if d % A == target_mod:
            y = (nx + d) // A
            z = (nx + nx * nx // d) // A
            if y > 0 and z > 0 and 4 * x * y * z == n * (x*y + x*z + y*z):
                return True, {"A": A}
    return False, None

def find_min_A(p, max_m=200):
    for m in range(max_m):
        A = 4 * m + 3
        ok, info = check_A(p, A)
        if ok:
            return info
    return None

def is_exceptional(p):
    c = (p + 3) // 4
    m = c
    q = 2
    while q * q <= m:
        if m % q == 0:
            if q % 3 == 2:
                return False
            while m % q == 0:
                m //= q
        q += 1 if q == 2 else 2
    if m > 1 and m % 3 == 2:
        return False
    return True

limit = 200000
print(f"Sieving primes up to {limit}...")
t0 = time.perf_counter()
is_p = [True] * (limit + 1)
is_p[0] = is_p[1] = False
for i in range(2, int(limit**0.5) + 1):
    if is_p[i]:
        step = i
        start = i * i
        is_p[start:limit+1:step] = [False] * ((limit - start) // step + 1)
primes = [i for i, v in enumerate(is_p) if v]
print(f"  {len(primes)} primes in {time.perf_counter()-t0:.1f}s")

# Find exceptional primes (faster: only check p ≡ 1 mod 12)
exceptional = []
for p in primes:
    if p < 13 or p % 12 != 1:
        continue
    if is_exceptional(p):
        exceptional.append(p)
print(f"  {len(exceptional)} exceptional primes")

# Solve each one
t0 = time.perf_counter()
results = []
max_m_found = 0
sum_m = 0
for idx, p in enumerate(exceptional):
    info = find_min_A(p, max_m=200)
    m = -1
    if info is not None:
        m = (info["A"] - 3) // 4
        if m > max_m_found:
            max_m_found = m
        sum_m += m
        results.append({"p": p, "A": info["A"], "m": m})
    else:
        results.append({"p": p, "A": 0, "m": -1})
        print(f"  FAILED p={p}")
    
    if (idx + 1) % 500 == 0:
        elapsed = time.perf_counter() - t0
        rate = (idx + 1) / elapsed
        print(f"  [{idx+1}/{len(exceptional)}] rate={rate:.0f}/s, solved={sum(1 for r in results if r['A']>0)}, max_m={max_m_found}")

elapsed = time.perf_counter() - t0
solved = [r for r in results if r["A"] > 0]
failed = [r for r in results if r["A"] == 0]
print(f"\n=== RESULTS ===")
print(f"Solved: {len(solved)}/{len(exceptional)} in {elapsed:.1f}s")
print(f"Failed: {len(failed)}")
if failed:
    print(f"  First few failures: {[r['p'] for r in failed[:10]]}")
print(f"Max minimal m: {max_m_found}")
print(f"Mean minimal m: {sum_m/len(solved):.2f}")

# Distribution of minimal m
from collections import Counter
m_dist = Counter()
A_dist = Counter()
for r in solved:
    m_dist[r["m"]] += 1
    A_dist[r["A"]] += 1

print(f"\nDistribution by m (A = 4m+3):")
for m_val in sorted(m_dist):
    A_val = 4 * m_val + 3
    print(f"  m={m_val:3d} (A={A_val:3d}): {m_dist[m_val]} ({m_dist[m_val]/len(solved)*100:.2f}%)")

# Show the top 10 highest m values
print(f"\nHighest minimal m values:")
high_m = sorted([r for r in solved], key=lambda x: -x["m"])[:20]
for r in high_m:
    print(f"  p={r['p']:6d}, A={r['A']:3d}, m={r['m']:3d}")

# Check what modulus separates all the groups
print(f"\n--- SEARCHING FOR SEPARATING MODULUS ---")
groups = {}
for r in solved:
    groups.setdefault(r["A"], []).append(r["p"])

for mod in range(3, 3001):
    mod_sets = {}
    for A, plist in groups.items():
        mod_sets[A] = set(p % mod for p in plist)
    disjoint = True
    A_list = list(mod_sets.keys())
    for i in range(len(A_list)):
        for j in range(i+1, len(A_list)):
            if not mod_sets[A_list[i]].isdisjoint(mod_sets[A_list[j]]):
                disjoint = False
                break
        if not disjoint:
            break
    if disjoint:
        print(f"  mod {mod} separates ALL minimal A groups!")
        for A in sorted(groups):
            print(f"    A={A}: {sorted(mod_sets[A])}")
        break
else:
    print(f"  No single modulus up to 3000 separates all groups")
