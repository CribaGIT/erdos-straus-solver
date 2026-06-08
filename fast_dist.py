"""Fast distribution analysis — no A limit."""
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
                return True, {"A": A, "x": x, "y": y, "z": z, "d": d}
    return False, None

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

# ================================================================
print("Sieving primes up to 10000...")
limit = 10000
is_p = [True] * (limit + 1)
is_p[0] = is_p[1] = False
for i in range(2, int(limit**0.5) + 1):
    if is_p[i]:
        step = i
        start = i * i
        is_p[start:limit+1:step] = [False] * ((limit - start) // step + 1)
primes = [i for i, v in enumerate(is_p) if v]
print(f"  {len(primes)} primes")

exceptional = [p for p in primes if p >= 13 and p % 12 == 1 and is_exceptional(p)]
print(f"  {len(exceptional)} exceptional primes up to {limit}")

# For each exceptional prime, try all possible A values
# Start with the most likely small A, then try 3p, 7p
t0 = time.perf_counter()
results = []
failures = []
for idx, p in enumerate(exceptional):
    candidates = sorted(set([3, 7, 11, 23, 3*p, 7*p]))
    found = None
    for A in candidates:
        ok, info = check_A(p, A)
        if ok:
            found = info
            break
    if found is None:
        failures.append(p)
        print(f"  FAILED p={p}")
    else:
        results.append({"p": p, "found": found})
    if (idx + 1) % 10 == 0:
        elapsed = time.perf_counter() - t0
        rate = (idx + 1) / elapsed if elapsed > 0 else 0
        print(f"  [{idx+1}/{len(exceptional)}] {elapsed:.1f}s, {rate:.1f} cases/s")

elapsed = time.perf_counter() - t0
print(f"\nDone in {elapsed:.1f}s")
print(f"Solved: {len(results)}/{len(exceptional)}")
if failures:
    print(f"Failures: {failures}")

# Distribution
from collections import Counter
A_counter = Counter()
for r in results:
    A_counter[r["found"]["A"]] += 1

# Group by A value type
def classify_A(A, p):
    if A == p:
        return "A=p"
    if A == 3 * p:
        return "A=3p"
    if A == 7 * p:
        return "A=7p"
    if A in (3, 7, 11, 23):
        return f"A={A}"
    return f"A={A} (other)"

type_counter = Counter()
for r in results:
    t = classify_A(r["found"]["A"], r["p"])
    type_counter[t] += 1

print("\nDistribution by type:")
for t, count in sorted(type_counter.items(), key=lambda x: -x[1]):
    print(f"  {t:12s}: {count} ({count/len(results)*100:.1f}%)")

# For constant A values, check modular rules
for A_val in [7, 11, 23]:
    subset = [r for r in results if r["found"]["A"] == A_val]
    if not subset:
        continue
    print(f"\nA={A_val} ({len(subset)} cases):")
    mod84 = Counter()
    for r in subset:
        mod84[r["p"] % 84] += 1
    mod120 = Counter()
    for r in subset:
        mod120[r["p"] % 120] += 1
    print(f"  p mod 84: {dict(sorted(mod84.items()))}")
    top120 = sorted(mod120.items(), key=lambda x: -x[1])[:8]
    print(f"  p mod 120: {top120}")

# Group by p mod 84
print("\n--- GROUPING BY p mod 84 ---")
by_mod84 = {}
for r in results:
    mod84 = r["p"] % 84
    by_mod84.setdefault(mod84, []).append(r)
for mod84 in sorted(by_mod84):
    group = by_mod84[mod84]
    A_vals = set(r["found"]["A"] for r in group)
    if len(A_vals) > 1:
        print(f"  p%84={mod84:2d}: AMBIGUOUS A in {sorted(A_vals)}")
        for r in group[:5]:
            print(f"          p={r['p']:5d}, A={r['found']['A']}")
    else:
        A = list(A_vals)[0]
        print(f"  p%84={mod84:2d}: A={A} ({len(group)})")

# Check p mod 120
print("\n--- GROUPING BY p mod 120 ---")
by_mod120 = {}
for r in results:
    mod120 = r["p"] % 120
    by_mod120.setdefault(mod120, []).append(r)
for mod120 in sorted(by_mod120):
    group = by_mod120[mod120]
    A_vals = set(r["found"]["A"] for r in group)
    if len(A_vals) > 1:
        print(f"  p%120={mod120:3d}: AMBIGUOUS A in {sorted(A_vals)} ({len(group)} cases)")
    else:
        A = list(A_vals)[0]
        print(f"  p%120={mod120:3d}: A={A} ({len(group)})")

# Check p mod 168 (extra resolution)
print("\n--- GROUPING BY p mod 168 ---")
by_mod168 = {}
for r in results:
    mod168 = r["p"] % 168
    by_mod168.setdefault(mod168, []).append(r)
ambiguous168 = []
for mod168 in sorted(by_mod168):
    group = by_mod168[mod168]
    A_vals = set(r["found"]["A"] for r in group)
    if len(A_vals) > 1:
        ambiguous168.append((mod168, sorted(A_vals), len(group)))
if ambiguous168:
    print(f"  Ambiguous residues: {len(ambiguous168)}")
    for mod168, A_vals, n in ambiguous168[:15]:
        print(f"    p%168={mod168:3d}: A in {A_vals} ({n} cases)")
else:
    print("  No ambiguous residues!") 

# If still ambiguous, try p mod 840
if ambiguous168:
    print("\n--- GROUPING BY p mod 840 ---")
    by_mod840 = {}
    for r in results:
        mod840 = r["p"] % 840
        by_mod840.setdefault(mod840, []).append(r)
    ambiguous840 = 0
    for mod840 in sorted(by_mod840):
        group = by_mod840[mod840]
        A_vals = set(r["found"]["A"] for r in group)
        if len(A_vals) > 1:
            ambiguous840 += 1
            if ambiguous840 <= 10:
                sample = [r for r in group[:3]]
                print(f"    p%840={mod840:4d}: A in {sorted(A_vals)} ({len(group)} cases)")
    if ambiguous840 == 0:
        print("  MOD 840 PERFECTLY SEPARATES ALL CASES!")
    else:
        print(f"  Still ambiguous: {ambiguous840} residues at mod 840")
