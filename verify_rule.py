"""
VERIFY AND EXTEND: Compute the exact decision tree for minimal A.
Test hypotheses from the mod 259 analysis, then extend to 10^6.
"""
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

# Residue classification from mod 259 analysis
RESIDUES = {
    7: [6, 17, 26, 41, 47, 54, 55, 59, 61, 66, 69, 73, 82, 83, 89, 94, 101, 104, 110, 117, 129, 132, 136, 139, 145, 150, 152, 164, 166, 167, 174, 180, 192, 194, 195, 199, 209, 213, 223, 227, 237, 241, 243, 244, 250, 251, 255],
    11: [4, 9, 29, 57, 67, 72, 93, 109, 123, 155, 158, 165, 183, 190, 193, 198, 200, 205, 233, 256],
    15: [60, 65, 116, 141, 142, 242],
    19: [50, 99, 130, 162, 186, 214],
    23: [18],
    31: [176],
}

print("=== VERIFYING DECISION RULE ON ALL EXCEPTIONAL PRIMES UP TO 10000 ===")

limit = 10000
is_p = [True] * (limit + 1)
is_p[0] = is_p[1] = False
for i in range(2, int(limit**0.5) + 1):
    if is_p[i]:
        step = i
        start = i * i
        is_p[start:limit+1:step] = [False] * ((limit - start) // step + 1)
primes = [i for i, v in enumerate(is_p) if v]
exceptional = [p for p in primes if p >= 13 and p % 12 == 1 and is_exceptional(p)]

errors = []
for p in exceptional:
    info = find_min_A(p, max_m=200)
    if info is None:
        errors.append((p, "NOT SOLVED"))
        continue
    actual_A = info["A"]
    r = p % 259
    predicted_A = None
    for A in sorted(RESIDUES):
        if r in RESIDUES[A]:
            predicted_A = A
            break
    if predicted_A is None:
        errors.append((p, f"NO RULE for mod259={r}, actual A={actual_A}"))
    elif predicted_A != actual_A:
        errors.append((p, f"PREDICTED A={predicted_A} != ACTUAL A={actual_A}, mod259={r}"))

if errors:
    print(f"ERRORS: {len(errors)}")
    for p, msg in errors:
        print(f"  p={p}: {msg}")
else:
    print("ALL VERIFIED: decision rule by mod 259 is exact!")

# Simplified decision tree
A7_set = set(p % 7 for p in exceptional if find_min_A(p)["A"] == 7)
other_set = set(p % 7 for p in exceptional if find_min_A(p)["A"] != 7)
print(f"\nLevel 1 (p mod 7): A=7 when p%7 in {sorted(A7_set)}")
print(f"  else (p%7 in {sorted(other_set)}): check further")

non_A7 = [p for p in exceptional if find_min_A(p)["A"] != 7]
A11_set = set(p % 11 for p in non_A7 if find_min_A(p)["A"] == 11)
A15_set = set(p % 11 for p in non_A7 if find_min_A(p)["A"] == 15)
A19_set = set(p % 11 for p in non_A7 if find_min_A(p)["A"] == 19)
A23_set = set(p % 11 for p in non_A7 if find_min_A(p)["A"] == 23)
A31_set = set(p % 11 for p in non_A7 if find_min_A(p)["A"] == 31)

print(f"\nLevel 2 (p mod 11):")
print(f"  A=11: p%11 in {sorted(A11_set)}")
print(f"  A=15: p%11 in {sorted(A15_set)}")
print(f"  A=19: p%11 in {sorted(A19_set)}")
print(f"  A=23: p%11 in {sorted(A23_set)}")
print(f"  A=31: p%11 in {sorted(A31_set)}")

# Check for overlaps
all_sets = [("A=11", A11_set), ("A=15", A15_set), ("A=19", A19_set), ("A=23", A23_set), ("A=31", A31_set)]
for i in range(len(all_sets)):
    for j in range(i+1, len(all_sets)):
        name_i, set_i = all_sets[i]
        name_j, set_j = all_sets[j]
        overlap = set_i & set_j
        if overlap and set_i and set_j:
            print(f"  OVERLAP {name_i} vs {name_j}: {sorted(overlap)}")

# Level 3: within same mod 11, what separates?
same_mod11 = {}
for p in non_A7:
    info = find_min_A(p)
    m11 = p % 11
    same_mod11.setdefault(m11, []).append((p, info["A"]))

print("\nLevel 3 (within same mod 11):")
for m11 in sorted(same_mod11):
    pairs = same_mod11[m11]
    A_vals = set(A for _, A in pairs)
    if len(A_vals) > 1:
        by_A = {}
        for p, A in pairs:
            by_A.setdefault(A, []).append(p % 5)
        print(f"  p%11={m11}: A in {sorted(A_vals)}")
        for A, mod5_vals in sorted(by_A.items()):
            print(f"    A={A}: p%5 in {sorted(set(mod5_vals))}")

# Summary
print("\n=== SUMMARY ===")
for A in [7, 11, 15, 19, 23, 31]:
    count = sum(1 for p in exceptional if find_min_A(p)["A"] == A)
    print(f"  A={A:2d} (m={(A-3)//4}): {count} cases ({count/len(exceptional)*100:.1f}%)")

# =====================================================================
# EXTEND TO 10^6 via the residue rule (no actual solving needed)
# =====================================================================
print("\n=== EXTENDING TO 10^6 VIA RESIDUE RULE ===")
high_limit = 10**6
is_p_big = bytearray(b'\x01') * (high_limit + 1)
is_p_big[0] = is_p_big[1] = 0
for i in range(2, int(high_limit**0.5) + 1):
    if is_p_big[i]:
        step = i
        start = i * i
        is_p_big[start:high_limit+1:step] = b'\x00' * ((high_limit - start) // step + 1)

A_counts = {7: 0, 11: 0, 15: 0, 19: 0, 23: 0, 31: 0, "other": 0}
t0 = time.perf_counter()
last_report = 0
for p in range(13, high_limit + 1, 12):
    if not is_p_big[p]:
        continue
    if not is_exceptional(p):
        continue
    
    r = p % 259
    found = False
    for A in [7, 11, 15, 19, 23, 31]:
        if r in RESIDUES[A]:
            A_counts[A] += 1
            found = True
            break
    if not found:
        A_counts["other"] += 1
    
    last_report += 1
    if last_report % 10000 == 0:
        total_so_far = sum(A_counts.values())
        elapsed = time.perf_counter() - t0
        print(f"  [{total_so_far}] scanned, last p={p}, {elapsed:.0f}s")

elapsed = time.perf_counter() - t0
total = sum(A_counts.values())
print(f"\nTotal exceptional primes up to 10^6: {total}")
if A_counts["other"] > 0:
    print(f"UNMATCHED: {A_counts['other']}")
else:
    print("ALL CASES MATCH THE KNOWN RESIDUE CLASSES!")
print(f"\nDistribution by minimal A:")
for A in [7, 11, 15, 19, 23, 31]:
    print(f"  A={A:2d}: {A_counts[A]} ({A_counts[A]/total*100:.2f}%)")
print(f"Time: {elapsed:.1f}s")
