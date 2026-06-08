"""Efficient minimal-A scan for exceptional primes up to 10^7.
Uses precomputed prime list for fast trial-division factoring."""
import math, sys, time

# Precompute primes up to sqrt max_x = 10^7 / 2
PRIME_LIMIT = 5000000  # 5e6 > sqrt((10^14)/4) for p=10^7
def sieve(limit):
    is_p = bytearray(b'\x01') * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            step = i
            start = i * i
            is_p[start:limit+1:step] = b'\x00' * ((limit - start) // step + 1)
    return [i for i, v in enumerate(is_p) if v]

print(f"Sieving primes up to {PRIME_LIMIT}...")
t0 = time.perf_counter()
SMALL_PRIMES = sieve(PRIME_LIMIT)
print(f"  {len(SMALL_PRIMES)} primes in {time.perf_counter()-t0:.1f}s")

def factorize_fast(n, small_primes):
    """Factor n using precomputed small primes. Returns dict {prime: exponent}."""
    res = {}
    m = n
    for q in small_primes:
        if q * q > m:
            break
        if m % q == 0:
            cnt = 0
            while m % q == 0:
                m //= q
                cnt += 1
            res[q] = cnt
    if m > 1:
        res[m] = 1
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

def check_A_fast(p, A, small_primes):
    n = p * p
    if (n + A) % 4 != 0:
        return False, None
    x = (n + A) // 4
    nx = n * x
    target_mod = (-nx) % A
    fac = factorize_fast(x, small_primes)
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

def check_A_strict(p, A):
    """Strict check: only divisors of x, not x^2. Faster for common cases."""
    n = p * p
    if (n + A) % 4 != 0:
        return False, None
    x = (n + A) // 4
    nx = n * x
    target_mod = (-nx) % A
    # Enumerate divisors of x by iterating up to sqrt(x)
    # This avoids factoring when the number has few divisors
    max_d = int(x ** 0.5)
    d_vals = []
    for i in range(1, max_d + 1):
        if x % i == 0:
            d_vals.append(i)
            if i != x // i:
                d_vals.append(x // i)
    for d in d_vals:
        if d % A == target_mod:
            y = (nx + d) // A
            z = (nx + nx * nx // d) // A
            if y > 0 and z > 0 and 4 * x * y * z == n * (x*y + x*z + y*z):
                return True, {"A": A}
    return False, None

def find_min_A_fast(p, small_primes, max_m=200):
    """Try known A values first, then search further if needed."""
    known_A = [7, 11, 15, 19, 23, 31, 39, 43, 51]
    for A in known_A:
        ok, info = check_A_fast(p, A, small_primes)
        if ok:
            return info
    # Fallback: search all m up to max_m
    for m in range(max_m):
        A = 4 * m + 3
        if A in known_A:
            continue
        ok, info = check_A_fast(p, A, small_primes)
        if ok:
            return info
    return None

def is_exceptional(p, small_primes):
    c = (p + 3) // 4
    m = c
    fac = factorize_fast(m, small_primes)
    for q, e in fac.items():
        if q % 3 == 2:
            return False
    return True

# Sieve primes for main loop
PRIME_LIMIT_MAIN = 5000000  # just for exceptional checking
print("Sieving for prime testing...")
is_p = bytearray(b'\x01') * (PRIME_LIMIT_MAIN + 1)
is_p[0] = is_p[1] = 0
for i in range(2, int(PRIME_LIMIT_MAIN**0.5) + 1):
    if is_p[i]:
        step = i
        start = i * i
        is_p[start:PRIME_LIMIT_MAIN+1:step] = b'\x00' * ((PRIME_LIMIT_MAIN - start) // step + 1)

# Scanner: iterate p ≡ 1 mod 12 up to 10^7
MAX_P = 10_000_000
print(f"Scanning exceptional primes up to {MAX_P}...")
t0 = time.perf_counter()
results = []
count = 0
failed = 0
max_m = 0
sum_m = 0

for p in range(13, MAX_P + 1, 12):
    if p > PRIME_LIMIT_MAIN:
        # For p > 5e6, fall back to trial division primality check
        is_prime = True
        for q in SMALL_PRIMES:
            if q * q > p:
                break
            if p % q == 0:
                is_prime = False
                break
        if not is_prime:
            continue
    elif not is_p[p]:
        continue
    
    if not is_exceptional(p, SMALL_PRIMES):
        continue
    
    count += 1
    info = find_min_A_fast(p, SMALL_PRIMES, max_m=200)
    if info is None:
        failed += 1
        if failed <= 5:
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
        print(f"  [{count}/~?] rate={rate:.0f}/s, solved={count-failed}, max_m={max_m}, mean_m={mean_m:.2f}, p={p}")

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
    print(f"  m={m_val:3d} (A={A_val:3d}): {m_dist[m_val]:5d} ({pct:.2f}%)")

print(f"\nHighest minimal m values:")
for r in sorted(results, key=lambda x: -x["m"])[:20]:
    print(f"  p={r['p']:8d}, A={r['A']:3d}, m={r['m']:3d}")
