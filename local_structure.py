"""
Investigation: Local Structure of the Omega Solver
===================================================

For fixed A, the condition is:
  ∃ d | p⁴x²  such that  d ≡ -p²x (mod A)
where x = (p² + A)/4.

Question: Does this decompose into independent local conditions
modulo each prime power dividing A?

If A = ∏ q_i^{e_i}, then d ≡ -p²x (mod A) ⇔ d ≡ -p²x (mod q_i^{e_i}) ∀i.

For each prime power q^e || A, define:
  P_{q^e}(p) = "∃ d | p⁴x² such that d ≡ -p²x (mod q^e)"

Then P_A(p) = ∧_i P_{q_i^{e_i}}(p).

If each P_{q^e}(p) depends only on p modulo some M_{q^e},
then P_A(p) depends only on p modulo M_A = lcm_i M_{q_i^{e_i}}.

This script tests this for small A values.
"""

import math
from collections import Counter

def factorize(n):
    m = n; res = {}; q = 2
    while q * q <= m:
        while m % q == 0:
            res[q] = res.get(q, 0) + 1; m //= q
        q += 1 if q == 2 else 2
    if m > 1:
        res[m] = res.get(m, 0) + 1
    return res

def divisors_from_factors(factors):
    divs = [1]
    for prime, exp in factors.items():
        cur = []; p_pow = 1
        for _ in range(exp + 1):
            for d in divs: cur.append(d * p_pow)
            p_pow *= prime
        divs = cur
    return divs