"""Generate b-files for OEIS submission:
   b-file 1: sequence of distinct A-values (22 terms)
   b-file 2: minimal A for first N exceptional primes
"""
import math
import random
import sys

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
    if n == 1:
        return {}
    res = {}
    m = n
    TRIAL_LIMIT = 10000
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

def check_A(p, A):
    n = p * p
    if (n + A) % 4 != 0:
        return False
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
                return True
    return False

def find_min_A(p, max_m=200):
    known_A = [7, 11, 15, 19, 23, 31, 39, 43, 47, 51, 59, 67, 71, 79, 83, 87, 95, 103, 107, 111, 127, 159]
    for A in known_A:
        if check_A(p, A):
            return A
    for m in range(max_m):
        A = 4 * m + 3
        if A in known_A:
            continue
        if check_A(p, A):
            return A
    return None

def is_exceptional(p):
    c = (p + 3) // 4
    fac = factorize_full(c)
    for q in fac:
        if q % 3 == 2:
            return False
    return True

def generate_bfile_exceptional(max_n_terms, output_file):
    """Generate b-file of A-values for first max_n_terms exceptional primes."""
    init_small_primes(5000000)

    # Sieve primes up to reasonable limit
    sieve_limit = 50000000
    print("Sieving primes...")
    is_p = bytearray(b'\x01') * (sieve_limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(sieve_limit**0.5) + 1):
        if is_p[i]:
            step = i
            start = i * i
            is_p[start:sieve_limit+1:step] = b'\x00' * ((sieve_limit - start) // step + 1)

    print(f"Scanning for exceptional primes (need {max_n_terms} terms)...")
    count = 0
    with open(output_file, 'w') as f:
        for p in range(13, sieve_limit + 1, 12):
            if not is_p[p]:
                continue
            if not is_exceptional(p):
                continue
            count += 1
            A = find_min_A(p)
            if A is None:
                print(f"ERROR: No A found for p={p}")
                f.write(f"{count} 0  # FAILED p={p}\n")
            else:
                f.write(f"{count} {A}\n")
            if count % 100 == 0:
                print(f"  [{count}] p={p}, A={A}")
            if count >= max_n_terms:
                break

    print(f"Wrote {count} terms to {output_file}")


if __name__ == '__main__':
    import random  # needed for miller_rabin/pollard_rho
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 100
    generate_bfile_exceptional(n, f"bfile_exceptional_{n}.txt")
    print("Done")
