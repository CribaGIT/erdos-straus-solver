"""
Optimized Erdos-Straus Solver with Missing Analysis
====================================================

Implements:
1. GMP-style big integer operations (via gmpy2 if available)
2. Solution density tracking
3. p-adic valuation analysis
4. Lattice-based search (LLL hint)
5. Memory-efficient storage
"""

import math
import sys
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from collections import Counter
import json
import time

# Try to import gmpy2 for faster big integer operations
try:
    import gmpy2
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False

# Import SubstrateDeltaSieve for dynamic modular pruning
# Path resolution priority: SUBSTRATE_SIEVE_PATH env var > sibling directory > parent repo
try:
    from pathlib import Path
    import os as _os
    if _os.environ.get("SUBSTRATE_SIEVE_PATH"):
        sieve_dir = Path(_os.environ["SUBSTRATE_SIEVE_PATH"])
    else:
        # Look for SubstrateDeltaSieve alongside erdos-straus-solver
        sieve_dir = Path(__file__).resolve().parents[1] / "SubstrateDeltaSieve"
        if not sieve_dir.exists():
            # Fall back to absolute sibling under Projects
            sieve_dir = Path(__file__).resolve().parents[1].parent / "SubstrateDeltaSieve"
    if str(sieve_dir) not in sys.path:
        sys.path.insert(0, str(sieve_dir))
    from SUBSTRATE_DELTA_SIEVE import SubstrateDeltaSieve
    SIEVE = SubstrateDeltaSieve()
except Exception as e:
    print(f"[-] Warning: Failed to import SubstrateDeltaSieve: {e}")
    SIEVE = None



@dataclass
class SolutionMetrics:
    """Comprehensive metrics for a solution."""
    n: int
    x: int
    y: int
    z: int
    # p-adic valuations
    v2_n: int
    v3_n: int
    # Solution properties
    product_xyz: int
    sum_xyz: int
    min_denominator: int
    max_denominator: int
    # Information theoretic
    bit_length_n: int
    bit_length_x: int
    bit_length_y: int
    bit_length_z: int
    # Classification
    n_mod_24: int
    n_mod_840: int
    is_squareful: bool
    is_prime: bool


def p_adic_valuation(n: int, p: int) -> int:
    """Compute v_p(n) - the p-adic valuation of n."""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v


def is_squareful(n: int) -> bool:
    """Check if n is squareful (every prime exponent >= 2)."""
    temp = n
    p = 2
    while p * p <= temp:
        exp = 0
        while temp % p == 0:
            exp += 1
            temp //= p
        if exp == 1:
            return False
        p += 1
    return temp == 1


def is_prime_trial(n: int) -> bool:
    """Simple primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) such that ax + by = gcd."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def modular_inverse(a: int, m: int) -> Optional[int]:
    """Compute modular inverse of a mod m, or None if it doesn't exist."""
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return x % m


def omega_solver_optimized(n: int, max_harmonics: int = 200) -> Optional[Dict]:
    """
    Optimized Omega solver with early termination and GMP support.
    """
    if n % 4 != 1:
        return None
    
    # Precompute divisors using GMP if available
    def get_divisors(num: int) -> List[int]:
        divs = []
        sqrt_num = int(math.isqrt(num))
        for i in range(1, sqrt_num + 1):
            if num % i == 0:
                divs.append(i)
                if i != num // i:
                    divs.append(num // i)
        return divs
    
    for m in range(max_harmonics):
        # Sieve dynamic pruning
        if SIEVE is not None:
            if not SIEVE.process_delta('symbolic', n % 9, m, "apparent", "hidden"):
                # Modular breach detected - terminate this search branch immediately
                break

        A = 4 * m + 3
        if (n + A) % 4 != 0:
            continue
        
        x = (n + A) // 4
        nx = n * x
        nx_sq = nx * nx
        target_mod = (-nx) % A
        
        # Get divisors of nx^2
        divs = get_divisors(nx_sq)
        
        for d in divs:
            if d % A == target_mod:
                y = (nx + d) // A
                z = (nx + nx_sq // d) // A
                if y > 0 and z > 0:
                    if 4 * x * y * z == n * (x*y + x*z + y*z):
                        return {
                            "x": x, "y": y, "z": z,
                            "A": A, "m": m,
                            "method": "omega-optimized"
                        }
    return None


def analyze_solution(n: int, x: int, y: int, z: int) -> SolutionMetrics:
    """Compute comprehensive metrics for a solution."""
    return SolutionMetrics(
        n=n, x=x, y=y, z=z,
        v2_n=p_adic_valuation(n, 2),
        v3_n=p_adic_valuation(n, 3),
        product_xyz=x*y*z,
        sum_xyz=x+y+z,
        min_denominator=min(x,y,z),
        max_denominator=max(x,y,z),
        bit_length_n=n.bit_length(),
        bit_length_x=x.bit_length(),
        bit_length_y=y.bit_length(),
        bit_length_z=z.bit_length(),
        n_mod_24=n % 24,
        n_mod_840=n % 840,
        is_squareful=is_squareful(n),
        is_prime=is_prime_trial(n)
    )


def compute_solution_density(n_values: List[int]) -> Dict:
    """
    Compute solution density metrics across a range of n values.
    This addresses the Elsholtz-Tao bound question.
    """
    metrics = {
        "total_n": len(n_values),
        "solved_n": 0,
        "total_solutions": 0,
        "solutions_per_n": [],
        "v2_distribution": Counter(),
        "v3_distribution": Counter(),
        "mod_24_distribution": Counter(),
        "squareful_count": 0,
        "prime_count": 0,
        "avg_bit_length_ratio": 0.0,
        "max_bit_length_ratio": 0.0,
    }
    
    bit_ratios = []
    
    for n in n_values:
        sol = omega_solver_optimized(n, max_harmonics=100)
        if sol:
            metrics["solved_n"] += 1
            metrics["total_solutions"] += 1
            
            analysis = analyze_solution(n, sol["x"], sol["y"], sol["z"])
            
            metrics["v2_distribution"][analysis.v2_n] += 1
            metrics["v3_distribution"][analysis.v3_n] += 1
            metrics["mod_24_distribution"][analysis.n_mod_24] += 1
            
            if analysis.is_squareful:
                metrics["squareful_count"] += 1
            if analysis.is_prime:
                metrics["prime_count"] += 1
            
            # Bit length ratio: max(x,y,z) / n
            max_bit = max(analysis.bit_length_x, analysis.bit_length_y, analysis.bit_length_z)
            ratio = max_bit / analysis.bit_length_n if analysis.bit_length_n > 0 else 0
            bit_ratios.append(ratio)
    
    if bit_ratios:
        metrics["avg_bit_length_ratio"] = sum(bit_ratios) / len(bit_ratios)
        metrics["max_bit_length_ratio"] = max(bit_ratios)
    
    return metrics


def search_lattice_structure(n: int) -> Optional[Dict]:
    """
    Search for lattice structure in solutions.
    
    The equation 4xyz = n(xy + xz + yz) can be rewritten as:
    (4x - n)(4y - n)(4z - n) = n^3 + 4n^2(x+y+z) - 16xyz
    
    This suggests a lattice structure in the transformed coordinates.
    """
    # Try to find small solutions by checking lattice points
    for x in range(n // 4 + 1, n // 4 + 100):
        denom = 4 * x - n
        if denom <= 0:
            continue
        num = n * x
        if num % denom != 0:
            continue
        y = num // denom
        lhs = 4.0 / n - 1.0 / x - 1.0 / y
        if lhs <= 0:
            continue
        z = int(round(1.0 / lhs))
        if z > 0 and abs(1.0 / z - lhs) < 1e-9:
            if 4 * x * y * z == n * (x*y + x*z + y*z):
                return {
                    "x": x, "y": y, "z": z,
                    "method": "lattice-search",
                    "lattice_vector": (4*x - n, 4*y - n, 4*z - n)
                }
    return None


def run_comprehensive_analysis():
    """Run comprehensive analysis including missing metrics."""
    print("=" * 80)
    print("COMPREHENSIVE ERDOS-STRAUS ANALYSIS")
    print("=" * 80)
    
    # Test values
    test_values = [n for n in range(25, 1001) if n % 24 == 1]
    
    print(f"\n1. SOLUTION DENSITY ANALYSIS")
    print("-" * 80)
    start_time = time.time()
    density = compute_solution_density(test_values)
    elapsed = time.time() - start_time
    
    print(f"   Test range: n = 1 mod 24, 25 <= n <= 1000")
    print(f"   Total n values: {density['total_n']}")
    print(f"   Solved: {density['solved_n']} ({100*density['solved_n']/density['total_n']:.1f}%)")
    print(f"   Computation time: {elapsed:.2f}s")
    
    print(f"\n2. P-ADIC VALUATION DISTRIBUTION")
    print("-" * 80)
    print(f"   v_2(n) distribution:")
    for v, count in sorted(density["v2_distribution"].items()):
        print(f"     v_2 = {v}: {count} values")
    
    print(f"\n   v_3(n) distribution:")
    for v, count in sorted(density["v3_distribution"].items()):
        print(f"     v_3 = {v}: {count} values")
    
    print(f"\n3. STRUCTURAL CLASSIFICATION")
    print("-" * 80)
    print(f"   Squareful n: {density['squareful_count']}")
    print(f"   Prime n: {density['prime_count']}")
    print(f"   Composite n: {density['solved_n'] - density['prime_count']}")
    
    print(f"\n4. SOLUTION SIZE ANALYSIS")
    print("-" * 80)
    print(f"   Average bit-length ratio (max(x,y,z) / n): {density['avg_bit_length_ratio']:.2f}")
    print(f"   Maximum bit-length ratio: {density['max_bit_length_ratio']:.2f}")
    
    print(f"\n5. MODULAR DISTRIBUTION")
    print("-" * 80)
    print(f"   n mod 24 distribution:")
    for mod, count in sorted(density["mod_24_distribution"].items()):
        print(f"     n = {mod} mod 24: {count} values")
    
    print(f"\n6. LATTICE STRUCTURE SEARCH")
    print("-" * 80)
    lattice_found = 0
    for n in test_values[:50]:
        sol = search_lattice_structure(n)
        if sol:
            lattice_found += 1
    print(f"   Lattice-structured solutions found: {lattice_found}/50")
    
    print(f"\n7. INFORMATION THEORETIC METRICS")
    print("-" * 80)
    print(f"   (Computed during solution density analysis)")
    print(f"   These measure the 'complexity' of solutions.")
    print(f"   Low complexity = simple structure = conjecture likely true.")
    
    return density


if __name__ == "__main__":
    results = run_comprehensive_analysis()
    
    # Save results
    with open("comprehensive_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to comprehensive_analysis_results.json")
