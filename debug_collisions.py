"""Debug: check if exceptional primes collide in small moduli."""
import math
from collections import Counter

def is_exceptional(p):
    if p % 12 != 1:
        return False
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

def sieve_exceptional(limit):
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0:2] = b'\x00\x00'
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            step = i
            start = i * i
            is_prime[start:limit+1:step] = b'\x00' * ((limit - start) // step + 1)
    exceptional = []
    for p in range(13, limit + 1):
        if is_prime[p] and is_exceptional(p):
            exceptional.append(p)
    return exceptional

limit = 2000000
print(f"Sieving exceptional primes up to {limit:,}...")
exc = sieve_exceptional(limit)
print(f"Found {len(exc)} exceptional primes")

for M in [77, 259, 385, 5005, 85085]:
    residues = [p % M for p in exc]
    unique = len(set(residues))
    total = len(residues)
    collisions = total - unique
    counter = Counter(residues)
    max_collisions = max(counter.values())
    expected = total * total / (2 * M)
    print(f"  M={M:>6}: {unique:>5} unique / {total:>5} total, {collisions} collisions, max={max_collisions}, expected_collisions~{expected:.1f}")
    if max_collisions > 2:
        for r, c in counter.most_common(5):
            if c >= 3:
                print(f"         residue {r} has {c} primes")

# Verify M=85085 collision count with explicit check
print()
print("DEBUG: M=85085 collision check (explicit):")
res85085 = Counter()
for p in exc:
    r = p % 85085
    res85085[r] += 1
unique = len(res85085)
total_collisions = sum(c - 1 for c in res85085.values())
classes_with_2plus = sum(1 for c in res85085.values() if c >= 2)
print(f"  Unique residues: {unique} / {len(exc)} total")
print(f"  Total collisions: {total_collisions}")
print(f"  Classes with 2+ primes: {classes_with_2plus}")
if classes_with_2plus:
    for r, c in res85085.most_common(5):
        if c >= 2:
            print(f"    r={r}: {c} primes, e.g. {[p for p in exc if p % 85085 == r][:3]}")
else:
    print("  (surprising - no collisions at all!)")
    # Check: how many valid residues are there for p ≡ 1 mod 12?
    valid = sum(1 for r in range(85085) if r % 12 == 1)
    print(f"  Valid residues (p ≡ 1 mod 12): {valid}")
    print(f"  So with {len(exc)} primes, expected collisions ~ {len(exc) - valid}")

# Check: do exceptional primes have p % 85,085 with any special property?
print()
print("DEBUG: Finding any collisions in M=85085 explicitly:")
# Search for pairs with same residue
seen = {}
for p in exc:
    r = p % 85085
    if r in seen:
        print(f"  COLLISION: {seen[r]} and {p} both have r={r}")
        break
    seen[r] = p
else:
    print("  No collisions found among all 8409 primes!")
    print("  This means every prime has a unique residue mod 85085.")
    print("  But there are only 7091 valid residues for p ≡ 1 mod 12.")
    print()
    print("  Verifying: first 10 residues and p values:")
    for i, p in enumerate(exc[:10]):
        r = p % 85085
        print(f"    p={p:>7}, r={r:>5}, r%12={r%12}, p%12={p%12}")
    print()
    print("  Checking k=12 spacing (to find collisions):")
    r = exc[0] % 85085
    for k in range(1, 24):
        pk = r + k * 85085
        if pk > exc[-1]:
            break
        if pk in exc:
            print(f"    k={k}: p={pk} shares r={r} with p={exc[0]}")
