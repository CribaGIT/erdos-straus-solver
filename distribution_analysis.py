"""
DISTRIBUTION ANALYSIS: Omega's A choices for exceptional p = 1 mod 12 primes.
Goal: identify exact modular rules governing which A in {3,7,11,23,3p,7p} is selected.

Uses the correct d | nx^2 condition throughout.
"""
import sys, math, time
sys.path.insert(0, '.')
from delta_analysis import omega_solve

def is_exceptional(p):
    """True if c = (p+3)/4 has no prime factor == 2 mod 3."""
    c = (p + 3) // 4
    m = c
    # Check primes up to sqrt(c)
    for q in [2] + list(range(3, int(math.isqrt(m)) + 1, 2)):
        if m % q == 0:
            if q % 3 == 2:
                return False
            while m % q == 0:
                m //= q
    if m > 1 and m % 3 == 2:
        return False
    return True

def prime_factors_to_2mod3(n):
    """Return the list of prime factors of n that are == 2 mod 3."""
    result = []
    m = n
    for q in [2] + list(range(3, int(math.isqrt(m)) + 1, 2)):
        if m % q == 0:
            if q % 3 == 2:
                result.append(q)
            while m % q == 0:
                m //= q
    if m > 1 and m % 3 == 2:
        result.append(m)
    return result

print("=" * 80)
print("TIER 3 EXCEPTIONAL CASE ANALYSIS: p = 1 mod 12")
print("=" * 80)

# Build sieve for primes up to 10^6
print("Sieving primes up to 10^6...")
t0 = time.perf_counter()
limit = 10**6
is_prime = [True] * (limit + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, int(limit**0.5) + 1):
    if is_prime[i]:
        step = i
        start = i * i
        is_prime[start:limit+1:step] = [False] * ((limit - start) // step + 1)
primes = [i for i, v in enumerate(is_prime) if v]
print(f"  Found {len(primes)} primes in {time.perf_counter()-t0:.1f}s")

# Collect exceptional primes
exceptional = [p for p in primes if p >= 13 and p % 12 == 1 and is_exceptional(p)]
print(f"  Exceptional primes (p = 1 mod 12, c no 2-mod-3 factor): {len(exceptional)}")

if not exceptional:
    print("  No exceptional primes found!")
    sys.exit(0)

# Test each with Omega and record the A value
print(f"Testing Omega on {len(exceptional)} exceptional primes (h=200)...")
t0 = time.perf_counter()

results = []
for i, p in enumerate(exceptional):
    n = p * p
    om = omega_solve(n, max_harmonics=200)
    if not om:
        print(f"  FAILED: p={p} at h=200!")
        continue
    
    A = om['A']
    m = (A - 3) // 4
    x = om['x']
    d = om['d']
    
    # Classify A
    if A == p:
        regime = "A=p"
    elif A == 3*p:
        regime = "A=3p"
    elif A == 7*p:
        regime = "A=7p"
    elif A in (3, 7, 11, 23):
        regime = f"A={A}"
    else:
        regime = f"A={A} (other)"
    
    # Compute modular residues
    mods = {
        "mod3": p % 3,
        "mod4": p % 4,
        "mod7": p % 7,
        "mod8": p % 8,
        "mod12": p % 12,
        "mod24": p % 24,
        "mod84": p % 84,
        "mod120": p % 120,
    }
    
    # What are c's prime factors?
    c = (p + 3) // 4
    c_factors_2mod3 = prime_factors_to_2mod3(c)
    
    results.append({
        "p": p,
        "A": A,
        "m": m,
        "regime": regime,
        "c": c,
        "c_factors_2mod3": c_factors_2mod3,
        "x": x,
        "n_plus_A": n + A,
        "mods": mods,
    })
    
    if (i+1) % 1000 == 0:
        print(f"  ... {i+1}/{len(exceptional)} ({(i+1)/len(exceptional)*100:.0f}%)")

elapsed = time.perf_counter() - t0
print(f"  Done in {elapsed:.1f}s ({elapsed/len(exceptional)*1000:.1f}ms per case)")

# Distribution by regime
print()
print("=" * 80)
print("DISTRIBUTION OF A VALUES")
print("=" * 80)
regime_counts = {}
for r in results:
    regime_counts[r["regime"]] = regime_counts.get(r["regime"], 0) + 1

for regime, count in sorted(regime_counts.items(), key=lambda x: -x[1]):
    pct = count / len(results) * 100
    print(f"  {regime:12s}: {count:5d} ({pct:5.1f}%)")

# For the constant A values (3, 7, 11, 23), check modular correlations
print()
print("=" * 80)
print("MODULAR ANALYSIS: What determines A in {3, 7, 11, 23}?")
print("=" * 80)

for const_A in [3, 7, 11, 23]:
    subset = [r for r in results if r["A"] == const_A]
    if not subset:
        print(f"\nA={const_A}: 0 cases")
        continue
    
    print(f"\nA={const_A}: {len(subset)} cases")
    
    # Check mod 7 correlation (A=7 case)
    if const_A == 7:
        mod7_counts = {}
        for r in subset:
            mod7 = r["mods"]["mod7"]
            mod7_counts[mod7] = mod7_counts.get(mod7, 0) + 1
        print(f"  p mod 7 distribution: {dict(sorted(mod7_counts.items()))}")
    
    # Check mod 3
    mod3_counts = {}
    for r in subset:
        mod3 = r["mods"]["mod3"]
        mod3_counts[mod3] = mod3_counts.get(mod3, 0) + 1
    print(f"  p mod 3: {dict(sorted(mod3_counts.items()))}")
    
    # Check mod 8
    mod8_counts = {}
    for r in subset:
        mod8 = r["mods"]["mod8"]
        mod8_counts[mod8] = mod8_counts.get(mod8, 0) + 1
    print(f"  p mod 8: {dict(sorted(mod8_counts.items()))}")
    
    # Check mod 24
    mod24_counts = {}
    for r in subset:
        mod24 = r["mods"]["mod24"]
        mod24_counts[mod24] = mod24_counts.get(mod24, 0) + 1
    print(f"  p mod 24: {dict(sorted(mod24_counts.items()))}")
    
    # Check mod 84 (7*12)
    mod84_counts = {}
    for r in subset:
        mod84 = r["mods"]["mod84"]
        mod84_counts[mod84] = mod84_counts.get(mod84, 0) + 1
    top84 = sorted(mod84_counts.items(), key=lambda x: -x[1])[:5]
    print(f"  p mod 84 (top 5): {top84}")
    
    # Check mod 120 (various small factors)
    mod120_counts = {}
    for r in subset:
        mod120 = r["mods"]["mod120"]
        mod120_counts[mod120] = mod120_counts.get(mod120, 0) + 1
    top120 = sorted(mod120_counts.items(), key=lambda x: -x[1])[:5]
    print(f"  p mod 120 (top 5): {top120}")
    
    # Check p^2 + A factorization
    even_count = sum(1 for r in subset if r["n_plus_A"] % 2 == 0)
    div4_count = sum(1 for r in subset if r["n_plus_A"] % 4 == 0)
    div8_count = sum(1 for r in subset if r["n_plus_A"] % 8 == 0)
    div_A_count = sum(1 for r in subset if r["n_plus_A"] % const_A == 0)
    print(f"  (n+A) % 2 = 0: {even_count}/{len(subset)}")
    print(f"  (n+A) % 4 = 0: {div4_count}/{len(subset)}")
    print(f"  (n+A) % 8 = 0: {div8_count}/{len(subset)}")
    print(f"  (n+A) % {const_A} = 0: {div_A_count}/{len(subset)}")

# Now try to find exact modular rules
print()
print("=" * 80)
print("MODULAR RULE DISCOVERY")
print("=" * 80)

# For each choice of A, find the minimal modular condition that predicts it
# Check: does A=3 always work when p ≡ 5 mod 12?
print("\nTesting hypothesis: A=3 when p ≡ 5 mod 12 (i.e., p ≡ 2 mod 3)")
A3_subset = [r for r in results if r["A"] == 3]
if A3_subset:
    all_mod5_mod12 = all(r["mods"]["mod12"] == 5 for r in A3_subset)
    print(f"  A=3 cases all have p ≡ 5 mod 12? {all_mod5_mod12}")
    if not all_mod5_mod12:
        print(f"  Exceptions: {[r['p'] for r in A3_subset if r['mods']['mod12'] != 5][:5]}")

# Check: do A=7 and A=11 split by p mod 7 or p mod 11?
print("\nTesting A=7 vs A=11 split:")
A7 = [r for r in results if r["A"] == 7]
A11 = [r for r in results if r["A"] == 11]
if A7 and A11:
    # Check if A=7 correlates with 7 | (p^2+7)
    A7_div7 = sum(1 for r in A7 if r["n_plus_A"] % 7 == 0)
    A11_div7 = sum(1 for r in A11 if r["n_plus_A"] % 7 == 0)
    print(f"  A=7: (n+A) % 7 == 0 for {A7_div7}/{len(A7)}")
    print(f"  A=11: (n+A) % 7 == 0 for {A11_div7}/{len(A11)}")
    
    # Check if p ≡ 1 mod 7 predicts A=7
    A7_p_mod7_1 = sum(1 for r in A7 if r["mods"]["mod7"] == 1)
    A11_p_mod7_1 = sum(1 for r in A11 if r["mods"]["mod7"] == 1)
    print(f"  A=7: p ≡ 1 mod 7 for {A7_p_mod7_1}/{len(A7)}")
    print(f"  A=11: p ≡ 1 mod 7 for {A11_p_mod7_1}/{len(A11)}")
    
    # Check p mod 84
    A7_mod84 = {}
    for r in A7:
        m = r["mods"]["mod84"]
        A7_mod84[m] = A7_mod84.get(m, 0) + 1
    A11_mod84 = {}
    for r in A11:
        m = r["mods"]["mod84"]
        A11_mod84[m] = A11_mod84.get(m, 0) + 1
    print(f"  A=7 unique mod84 residues: {sorted(A7_mod84.keys())}")
    print(f"  A=11 unique mod84 residues: {sorted(A11_mod84.keys())}")
    intersection = set(A7_mod84.keys()) & set(A11_mod84.keys())
    print(f"  Intersection: {sorted(intersection)}")
    if not intersection:
        print("  *** mod84 PERFECTLY SEPARATES A=7 vs A=11 ***")

# Now try to find the complete decision tree
print()
print("=" * 80)
print("ATTEMPTING COMPLETE DECISION TREE")
print("=" * 80)

# Partition results by regime
tiers = {}
for r in results:
    tiers.setdefault(r["regime"], []).append(r)

for regime, reg_results in sorted(tiers.items(), key=lambda x: -len(x[1])):
    print(f"\n{regime} ({len(reg_results)} cases):")
    # Show sample residues
    residue_sets = {}
    for modulus in [12, 24, 84, 120]:
        residues = set(r["mods"][f"mod{modulus}"] for r in reg_results)
        residue_sets[modulus] = residues
    print(f"  p mod 12: {sorted(residue_sets[12])}")
    if len(residue_sets[24]) < 20:
        print(f"  p mod 24: {sorted(residue_sets[24])}")
    if len(residue_sets[84]) < 30:
        print(f"  p mod 84: {sorted(residue_sets[84])}")
    
    # Show first 3 examples
    for r in reg_results[:3]:
        c_factors = r.get("c_factors_2mod3", [])
        print(f"    p={r['p']}, A={r['A']}, c={r['c']}, c_2mod3_factors={c_factors}")
