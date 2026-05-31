import pytest
from sieve_l40s_hot_corridor import erdos_straus_int, erdos_straus

def test_erdos_straus_int_known_values():
    # n = 4 should yield (1/x + 1/y + 1/z = 4/4 = 1) -> 4/4 = 1/2 + 1/3 + 1/6
    # For n=4, 4 % 4 == 0, Identity 1 applies: (3, 3, 3) because 1/3+1/3+1/3 = 1
    triples = erdos_straus_int(4)
    assert len(triples) > 0, "Failed to find solution for n=4"
    
    # Check if (3, 3, 3) is in triples (Identity 1)
    assert (3, 3, 3) in triples

    # Check mathematically that for each triple, 1/x + 1/y + 1/z == 4/n
    # Using integer arithmetic to avoid float precision issues:
    # 4/n = (y*z + x*z + x*y) / (x*y*z)
    # -> 4 * x * y * z == n * (y*z + x*z + x*y)
    n = 4
    for (x, y, z) in triples:
        left = 4 * x * y * z
        right = n * (y * z + x * z + x * y)
        assert left == right, f"Triple {x},{y},{z} is invalid for n={n}"

def test_erdos_straus_hot_corridor_filter():
    # Hot corridor target: mod24 == 0 and mod9 in {0, 3, 6}
    # E.g., 24 % 24 == 0, 24 % 9 == 6. Should be processed.
    n = 24
    has_sol, depth, triple, num_sol = erdos_straus(n)
    assert has_sol is True
    assert depth == "BREACH_MOD9"
    assert num_sol > 0
    
    # Check mathematical correctness
    x, y, z = triple
    left = 4 * x * y * z
    right = n * (y * z + x * z + x * y)
    assert left == right, f"Invalid triple returned by erdos_straus({n})"

def test_skip_non_hot_corridor():
    # n = 25 (not mod24 == 0)
    has_sol, depth, triple, num_sol = erdos_straus(25)
    assert has_sol is False
    assert depth == "SKIP"
    
    # n = 48, mod9 = 48 % 9 = 3 (this is a HOT_MOD9, mod24==0) -> Should pass
    has_sol, depth, triple, num_sol = erdos_straus(48)
    assert has_sol is True

    # n = 72, mod9 = 72 % 9 = 0 (HOT_MOD9, mod24==0) -> Should pass
    has_sol, depth, triple, num_sol = erdos_straus(72)
    assert has_sol is True
