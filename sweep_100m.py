"""Sweep to 10^8 with proper factoring (trial division + Pollard rho)."""
import math, sys, time, random

# ---------- factoring ----------
SMALL_PRIMES = []
PRIME_LIMIT = 5000000

def init_small_primes(limit):
    global SMALL_PRIMES, PRIME_LIMIT
    PRIME_LIMIT = limit
    is_p = bytearray(b'\x01') * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            step = i
            start = i * i
            is_p[start:limit+1:step] = b'\x00' * ((limit - start) // step + 1)
    SMALL_PRIMES = [i for i, v in enumerate(is_p) if v]

def miller_rabin(n, k=10):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def pollard_rho(n):
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    for c in range(1, 100):
        f = lambda x: (x * x + c) % n
        x = y = 2
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d
    return n

def factorize_full(n):
    """Factor any integer n using trial division + Pollard rho.
    
    Strategy: trial divide by first 10000 primes (fast), then use
    Miller-Rabin + Pollard rho for the remainder. Avoids full trial
    division up to sqrt(n) which is slow for large primes.
    """
    if n == 1:
        return {}
    res = {}
    m = n
    TRIAL_LIMIT = 10000  # check first ~1229 primes
    for q in SMALL_PRIMES[:TRIAL_LIMIT]:
        if q * q > m:
            break
        if m % q == 0:
            cnt = 0
            while m % q == 0:
                m //= q
                cnt += 1
            res[q] = cnt
    if m > 1:
        if miller_rabin(m):
            res[m] = 1
        else:
            stack = [m]
            while stack:
                x = stack.pop()
                if miller_rabin(x):
                    res[x] = res.get(x, 0) + 1
                else:
                    d = pollard_rho(x)
                    stack.append(d)
                    stack.append(x // d)
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

# ---------- Omega solver ----------
def check_A(p, A):
    n = p * p
    if (n + A) % 4 != 0:
        return False, None
    x = (n + A) // 4
    nx = n * x
    target_mod = (-nx) % A
    fac = factorize_full(x)
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
    known_A = [7, 11, 15, 19, 23, 31, 39, 43, 47, 51, 59, 67, 71, 79, 83, 87, 103]
    for A in known_A:
        ok, info = check_A(p, A)
        if ok:
            return info
    for m in range(max_m):
        A = 4 * m + 3
        if A in known_A:
            continue
        ok, info = check_A(p, A)
        if ok:
            return info
    return None

def is_exceptional(p):
    c = (p + 3) // 4
    fac = factorize_full(c)
    for q in fac:
        if q % 3 == 2:
            return False
    return True

# ---------- Main (only runs when executed directly) ----------
if __name__ != '__main__':
    # When imported, just set up small primes and return
    init_small_primes(5000000)
else:
    init_small_primes(5000000)
    print(f"Small primes: {len(SMALL_PRIMES)} up to {PRIME_LIMIT}")

    MAX_P = 100_000_000
    print(f"Scanning exceptional primes up to {MAX_P}...")

    # Sieve using faster slice-assignment approach
    t0 = time.perf_counter()
    print("Building primality sieve...")
    is_p = bytearray(b'\x01') * (MAX_P + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(MAX_P**0.5) + 1):
        if is_p[i]:
            step = i
            start = i * i
            is_p[start:MAX_P+1:step] = b'\x00' * ((MAX_P - start) // step + 1)
    print(f"  Sieve done in {time.perf_counter()-t0:.1f}s")

# Scan
results = []
count = 0
failed = 0
max_m = 0
sum_m = 0
sieve_check_count = 0

for p in range(13, MAX_P + 1, 12):
    if not is_p[p]:
        continue
    if not is_exceptional(p):
        continue
    
    count += 1
    info = find_min_A(p, max_m=200)
    if info is None:
        failed += 1
        print(f"  FAILED p={p}")
    else:
        m = (info["A"] - 3) // 4
        if m > max_m:
            max_m = m
            print(f"  NEW MAX m={m} at p={p}, A={info['A']}")
        sum_m += m
        results.append({"p": p, "A": info["A"], "m": m})
    
    if count % 2000 == 0:
        elapsed = time.perf_counter() - t0
        rate = count / elapsed if elapsed > 0 else 0
        mean_m = sum_m / count if count > 0 else 0
        print(f"  [{count}] rate={rate:.0f}/s, solved={count-failed}, max_m={max_m}, mean_m={mean_m:.2f}, p={p}")

elapsed = time.perf_counter() - t0
print(f"\n=== COMPLETE ===")
print(f"Scanned {count} exceptional primes in {elapsed:.1f}s")
print(f"Solved: {count - failed}/{count}")
print(f"Failed: {failed}")
print(f"Max minimal m: {max_m}")
print(f"Mean minimal m: {sum_m / count:.2f}")

from collections import Counter
m_dist = Counter()
A_dist = Counter()
for r in results:
    m_dist[r["m"]] += 1
    A_dist[r["A"]] += 1

print(f"\nDistribution by m (A = 4m+3):")
for m_val in sorted(m_dist):
    A_val = 4 * m_val + 3
    pct = m_dist[m_val] / count * 100
    print(f"  m={m_val:3d} (A={A_val:3d}): {m_dist[m_val]:6d} ({pct:.2f}%)")

print(f"\nHighest minimal m values:")
for r in sorted(results, key=lambda x: -x["m"])[:30]:
    print(f"  p={r['p']:9d}, A={r['A']:3d}, m={r['m']:3d}")
