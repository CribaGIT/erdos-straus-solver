# OEIS Submission: A-values for Exceptional Primes in Erdos-Straus Conjecture

## Sequence AXXXXXX (to be assigned)

**Name:** Minimal additive shifts A = 4m+3 for Tier 3 exceptional primes in the Erdos-Straus conjecture

**Data:**
7, 11, 15, 19, 23, 31, 39, 43, 47, 51, 59, 67, 71, 79, 83, 87, 95, 103, 107, 111, 127, 159

**Offset:** 1,1

**First term (n=1):** 7 (corresponds to m=1, first working shift)

**Last term listed:** 159 (A=159, m=39, observed at p=91,267,201)

**Description:**
Let p be a prime with p ≡ 1 (mod 12) such that c = (p+3)/4 has no prime factor ≡ 2 (mod 3). Such primes are "Tier 3 exceptional" for the Erdos-Straus equation 4/p^2 = 1/x + 1/y + 1/z. For each such p, the minimal additive shift A ≡ 3 (mod 4) such that x = (p^2 + A)/4 yields a valid solution via the divisor-congruence (Omega) method. This sequence lists all values of A that occur as the minimal working shift for at least one exceptional prime. Verified up to p ≤ 10^8 (289,372 exceptional primes), with 0 failures and max A = 159.

**Comments:**
- A = 4m+3 where m is the minimal number of harmonic steps
- 289,372 exceptional primes up to 10^8 are each solved by exactly one A from this set
- Mean minimal m = 2.25, median m = 1 (A=7 dominates at ~49.5%)
- Distribution: A=7 (49.5%), A=11 (22.6%), A=15 (9.4%), A=19 (8.9%), A=23 (4.8%), others (<4%)
- Certain A ≡ 3 mod 4 are never minimal: {3, 27, 35, 55, 63, 75, 91, 99, 115, 119, 123, 131, 135, 139, 143, 147, 151, 155}
- Max A grows slowly: A=51 at 10^5, A=71 at 10^6, A=111 at 10^7, A=159 at 10^8
- Bounded-A conjecture: all exceptional primes have A ≤ 159

**Formula:**
A = 4m + 3, where m is the minimal non-negative integer such that the Omega solver condition holds: there exists d | p^4 * x^2 with d ≡ -p^2 * x (mod A) and x = (p^2 + A)/4.

**Cross-references:**
Cf. A001358 (semiprimes), A005117 (squarefree numbers), Erdos-Straus conjecture (4/n = 1/x + 1/y + 1/z)

**Keywords:**
erdos-straus, egyptian-fractions, additive-shift, exceptional-primes, bounded-A

**Author:** DaShawn, Guinea Pig Trench LLC

**Submission date:** June 2026

**Data file:** See accompanying file `oeis_a_values_data.txt`

---

## Accompanying Data (`oeis_a_values_data.txt`)

```
# A sequence for Erdos-Straus Tier 3 exceptional primes
# Verified up to p <= 10^8 (289,372 primes, 0 failures)
#
# Format: A count percentage
7   143145  49.47
11   65251  22.55
15   27112   9.37
19   25644   8.86
23   13772   4.76
31    7459   2.58
39    3697   1.28
43    1325   0.46
47    1080   0.37
51     241   0.08
59     331   0.11
67      87   0.03
71     119   0.04
79      60   0.02
83      16  <0.01
87      12  <0.01
95       1  <0.01
103      8  <0.01
107      4  <0.01
111      5  <0.01
127      2  <0.01
159      1  <0.01
```

## Skipped A-values (A = 4m+3 that are never minimal)

```
A    m    Reason
3    0    A=3 works for all non-exceptional p ≡ 1 mod 4, but exceptional primes require larger A
27   6    Reduced to A=15 (m=3) via divisor reduction
35   8    Reduced to A=15 (m=3)
55   13   Reduced to A=11 (m=2)
63   15   Reduced to A=15 (m=3)
75   18   Reduced to A=15 (m=3)
91   22   Reduced to A=7 (m=1)
99   24   Reduced to A=15 (m=3)
115+     Multi-step reduction to smaller A
```
