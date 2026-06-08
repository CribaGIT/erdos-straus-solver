"""Analyze Omega's A choices for all n = p^2 up to p <= 500.
Goal: identify the pattern in additive shifts that defines the universal fallback.
"""
import sys, math
sys.path.insert(0, '.')
from delta_analysis import omega_solve, omega_divisors

def factor_str(n):
    """Return prime factorization as string."""
    if n == 1: return "1"
    m = n
    factors = []
    p = 2
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e > 0: factors.append(f"{p}^{e}" if e > 1 else str(p))
        p += 1 if p == 2 else 2
    if m > 1: factors.append(str(m))
    return "*".join(factors)

def divisor_count(n):
    """Number of divisors."""
    m = n
    cnt = 1
    p = 2
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e > 0: cnt *= (e + 1)
        p += 1 if p == 2 else 2
    if m > 1: cnt *= 2
    return cnt

print("=" * 80)
print("OMEGA's A CHOICES FOR n = p^2 — Additive Shift Analysis")
print("=" * 80)

# Collect data for all primes where p^2 = 1 mod 24
results = []
for p in range(5, 500, 2):
    # p must be prime
    is_prime = True
    for d in range(3, int(math.isqrt(p)) + 1, 2):
        if p % d == 0: is_prime = False; break
    if not is_prime: continue
    
    n = p * p
    if n % 24 != 1: continue
    
    # Case analysis
    p_mod_12 = p % 12
    
    om = omega_solve(n, max_harmonics=200)
    if not om:
        print(f"  p={p}: Omega FAILED at h=200!")
        continue
    
    A = om['A']
    m = (A - 3) // 4
    x = om['x']
    y = om['y']
    z = om['z']
    
    # Compute (n+A) = 4x, factor it
    n_plus_A = n + A
    dc = divisor_count(n_plus_A)
    
    # What formula regime?
    c4 = (p + 1) // 4  # for 4c-p = 1
    c4_test = (4*c4 - p == 1)
    c3 = (p + 3) // 4  # for 4c-p = 3
    c3_test = (4*c3 - p == 3)
    
    regime = ""
    if A == p and c4_test:
        regime = "A=p (4c-p=1)"
    elif A == 3*p and c3_test:
        regime = "A=3p (4c-p=3)"
    elif A % p == 0:
        regime = f"A={A//p}p"
    else:
        regime = f"A={A} (non-multiple)"
    
    results.append({
        "p": p, "n": n, "A": A, "m": m,
        "p_mod_12": p_mod_12,
        "n_plus_A": n_plus_A,
        "nA_divisor_count": dc,
        "regime": regime,
        "x": x, "y": y, "d": om['d'],
    })

# Group by regime
print(f"\nFound {len(results)} primes with p^2 = 1 mod 24, p <= 500")
print()

regimes = {}
for r in results:
    regimes.setdefault(r["regime"], []).append(r["p"])

print("Classification by A formula:")
for regime, primes in sorted(regimes.items()):
    print(f"  {regime}: {len(primes)} primes: {primes}")

# Analyze the "non-multiple" and "A=kp with k>3" cases
print()
print("=" * 80)
print("DETAILED ANALYSIS OF NON-STANDARD CASES")
print("=" * 80)
for r in results:
    if "A=3p" not in r["regime"] and "A=p" not in r["regime"]:
        # Factor (n+A)
        p = r["p"]
        nA = r["n_plus_A"]
        c3 = (p + 3) // 4
        c3_divs = [d for d in omega_divisors(c3*c3) if d % 3 == 2]
        print(f"\n  p={p} (mod 12 = {p%12}): A={r['A']} (m={r['m']}), regime={r['regime']}")
        print(f"    n+A = {p}² + {r['A']} = {nA} = {factor_str(nA)}")
        print(f"    divisor_count(n+A) = {r['nA_divisor_count']}")
        print(f"    c = (p+3)/4 = {c3}")
        print(f"    Divisors of c² == 2 mod 3: {c3_divs}")
        
        # What's the relationship between A and n?
        # A = 4m+3, so A ≡ 3 mod 4
        # A/p ratio
        print(f"    A/p = {r['A']/p:.2f}")
        
        # Check: is A the smallest working value?
        # Try smaller A values
        c = (r['x'] // p) if r['x'] % p == 0 else None
        print(f"    x/p integer? {r['x'] % p == 0}, x/p = {c}")

# Summarize the pattern
print()
print("=" * 80)
print("SUMMARY: A VALUE DISTRIBUTION")
print("=" * 80)
for p_mod in [1, 5, 7, 11]:
    sub = [r for r in results if r["p"] % 12 == p_mod]
    if sub:
        A_vals = [r["A"] for r in sub]
        m_vals = [r["m"] for r in sub]
        regimes_sub = {}
        for r in sub:
            regimes_sub[r["regime"]] = regimes_sub.get(r["regime"], 0) + 1
        print(f"p ≡ {p_mod} mod 12 ({len(sub)} primes):")
        print(f"  A values: min={min(A_vals)}, max={max(A_vals)}, median={sorted(A_vals)[len(A_vals)//2]}")
        print(f"  m (harmonics): min={min(m_vals)}, max={max(m_vals)}")
        print(f"  Regimes: {regimes_sub}")
        
        # For A != p and A != 3p — analyze the ratio A/p
        nonstd = [r for r in sub if r["regime"] not in ["A=p (4c-p=1)", "A=3p (4c-p=3)"]]
        if nonstd:
            print(f"  Non-standard cases:")
            for r in nonstd:
                print(f"    p={r['p']}: A={r['A']}, A/p={r['A']/r['p']:.2f}, m={r['m']}, n+A={factor_str(r['n_plus_A'])}")
        print()
