"""Minimal A analysis — show which primes get which A, check higher moduli."""
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

limit = 10000
print(f"Sieving primes up to {limit}...")
is_p = [True] * (limit + 1)
is_p[0] = is_p[1] = False
for i in range(2, int(limit**0.5) + 1):
    if is_p[i]:
        step = i
        start = i * i
        is_p[start:limit+1:step] = [False] * ((limit - start) // step + 1)
primes = [i for i, v in enumerate(is_p) if v]

exceptional = [p for p in primes if p >= 13 and p % 12 == 1 and is_exceptional(p)]
print(f"{len(exceptional)} exceptional primes up to {limit}")

t0 = time.perf_counter()
results = []
for idx, p in enumerate(exceptional):
    info = find_min_A(p, max_m=200)
    if info is None:
        print(f"  FAILED p={p}")
    else:
        results.append({"p": p, "A": info["A"], "m": (info["A"]-3)//4})
    if (idx + 1) % 20 == 0:
        print(f"  [{idx+1}/{len(exceptional)}]")

elapsed = time.perf_counter() - t0
print(f"Done in {elapsed:.1f}s — {len(results)}/{len(exceptional)} solved")

from collections import Counter

# Group by minimal A
m_counter = Counter()
for r in results:
    m_counter[r["m"]] += 1

print("\nMinimal A distribution (A = 4m+3):")
for m_val in sorted(m_counter):
    A_val = 4 * m_val + 3
    print(f"  m={m_val:3d} (A={A_val:3d}): {m_counter[m_val]}")

# For each A, list the primes and their p mod 2520
print("\n--- DETAILED LISTING ---")
for A_val in sorted(set(r["A"] for r in results)):
    subset = [r for r in results if r["A"] == A_val]
    print(f"\nA={A_val} ({len(subset)} cases):")
    mod2520 = Counter()
    for r in subset:
        mod2520[r["p"] % 2520] += 1
    for r in subset[:8]:
        print(f"  p={r['p']:5d}  m={r['m']}")
    print(f"  p mod 2520: {dict(sorted(mod2520.items()))}")

# Find modulus that perfectly separates the groups
print("\n--- SEARCHING FOR SEPARATING MODULUS ---")
groups = {}
for r in results:
    A = r["A"]
    groups.setdefault(A, []).append(r["p"])

# For each pair of groups, find minimal separating modulus
A_vals = sorted(groups.keys())
for i in range(len(A_vals)):
    for j in range(i+1, len(A_vals)):
        A1, A2 = A_vals[i], A_vals[j]
        for mod in range(3, 2001):
            set1 = set(p % mod for p in groups[A1])
            set2 = set(p % mod for p in groups[A2])
            if set1.isdisjoint(set2):
                print(f"  A={A1} vs A={A2}: mod {mod} separates perfectly")
                break
            if mod == 2000:
                print(f"  A={A1} vs A={A2}: NO separating modulus up to 2000")

# Check: can we find a single modulus that separates ALL groups?
print("\n--- SINGLE MODULUS FOR ALL GROUPS ---")
for mod in range(3, 2001):
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
        print(f"  mod {mod} separates ALL groups!")
        for A in sorted(groups):
            print(f"    A={A}: {sorted(mod_sets[A])}")
        break
else:
    print(f"  No single modulus up to 2000 separates all groups")

# Check if groups have any structure based on p^2 + A factorization
print("\n--- STRUCTURAL ANALYSIS ---")
for A_val in sorted(set(r["A"] for r in results)):
    subset = [r for r in results if r["A"] == A_val]
    print(f"\nA={A_val} ({len(subset)} cases):")
    for r in subset:
        p = r["p"]
        c = (p + 3) // 4
        # factor c
        fc = factorize(c)
        fc_str = "*".join(f"{q}^{e}" if e > 1 else str(q) for q, e in sorted(fc.items()))
        # factor n+A
        n_plus_A = p * p + A_val
        fn = factorize(n_plus_A)
        fn_str = "*".join(f"{q}^{e}" if e > 1 else str(q) for q, e in sorted(fn.items()))
        print(f"  p={p:5d} c={c:5d}={fc_str:20s} p^2+A={n_plus_A}={fn_str}")
