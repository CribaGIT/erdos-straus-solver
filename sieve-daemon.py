#!/usr/bin/env python3
"""
SIEVE DAEMON — Parallel Erdos-Straus solver with checkpoints.

Takes survivors from a sieve pass and solves 4/n = 1/x + 1/y + 1/z
in parallel. Checkpoints after every N solutions so you can CTRL+C
and resume.

Usage:
    python sieve-daemon.py survivors.txt
    python sieve-daemon.py survivors.txt --threads 8 --checkpoint 500
    python sieve-daemon.py survivors.txt --resume   # continue from checkpoint
"""

import sys
import json
import math
import time
import signal
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

CHECKPOINT_FILE = "sieve_checkpoint.json"
DEFAULT_THREADS = 4
CHECKPOINT_INTERVAL = 250


def solve_one(n: int):
    """Solve 4/n = 1/x + 1/y + 1/z for a single n. Returns (n, x, y, z) or None."""
    if n % 4 == 0:
        k = n // 4
        return (n, 3 * k, 3 * k, 3 * k)

    if n % 3 == 0:
        k = n // 3
        return (n, 2 * k, 2 * k, n)

    sqrt_n = int(n ** 0.5)
    search_limit = min(sqrt_n, 10_000_000)
    for d in range(1, search_limit + 1):
        if n % d != 0:
            continue
        for divisor in (d, n // d):
            if divisor > 10_000_000:
                continue
            x = divisor
            num = 4 * x - n
            if num <= 0:
                continue
            den = n * x
            g = math.gcd(num, den)
            a, b = num // g, den // g

            if a == 2:
                y = z = b
                if y >= x and z >= y:
                    return (n, x, y, z)
            elif a == 1:
                y = b + 1
                z = b * (b + 1)
                if y >= x and z >= y:
                    return (n, x, y, z)
            elif a == 3 and b % 2 == 0:
                y = b
                z = b // 2
                if y >= x and z >= y:
                    return (n, x, y, z)
    return None


def save_checkpoint(results, remaining, solved_count):
    """Save current state to resume later."""
    data = {
        "solved": solved_count,
        "remaining": list(remaining),
        "results": {str(n): r for n, *r in results if r},
        "timestamp": time.time(),
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def load_checkpoint():
    """Load saved state. Returns (results_dict, remaining_list, solved_count)."""
    if not Path(CHECKPOINT_FILE).exists():
        return {}, [], 0
    with open(CHECKPOINT_FILE) as f:
        data = json.load(f)
    results = {int(k): v for k, v in data["results"].items()}
    remaining = list(data["remaining"])
    return results, remaining, data["solved"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parallel Erdos-Straus sieve solver")
    parser.add_argument("survivors", nargs="?", help="Path to survivors file")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="Worker count")
    parser.add_argument("--checkpoint", type=int, default=CHECKPOINT_INTERVAL, help="Save every N solves")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    args = parser.parse_args()

    # Load survivors
    results = {}
    remaining = []
    solved = 0

    if args.resume:
        results, remaining, solved = load_checkpoint()
        print(f"[RESUME] {solved} solved, {len(remaining)} remaining")
        if not remaining:
            print("[DONE] No remaining survivors. All solved.")
            return
    else:
        if not args.survivors:
            print("Usage: sieve-daemon.py survivors.txt [--resume]")
            sys.exit(1)
        path = Path(args.survivors)
        if not path.exists():
            print(f"[ERR] Survivors file not found: {path}")
            sys.exit(1)
        with open(path) as f:
            all_ns = [int(line.strip()) for line in f if line.strip()]
        remaining = all_ns
        print(f"[LOAD] {len(remaining)} survivors loaded")

    # Handle CTRL+C gracefully
    shutdown = False

    def handler(sig, frame):
        nonlocal shutdown
        print("\n[SAVE] Signal received — saving checkpoint...")
        shutdown = True

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    start = time.time()
    batch = []
    batch_count = 0

    with ProcessPoolExecutor(max_workers=args.threads) as pool:
        futures = {}

        while remaining and not shutdown:
            # Fill the pool
            while len(futures) < args.threads * 2 and remaining:
                n = remaining.pop(0)
                futures[pool.submit(solve_one, n)] = n

            if not futures:
                break

            # Wait for one result
            done = next(as_completed(futures))
            n = futures.pop(done)
            try:
                r = done.result()
            except Exception as e:
                print(f"  [ERR] n={n}: {e}")
                continue

            if r:
                n_val, x, y, z = r
                results[n_val] = (x, y, z)
                solved += 1
                print(f"  ✓ 4/{n_val} = 1/{x} + 1/{y} + 1/{z}")
            else:
                print(f"  ✗ n={n} — no solution found in search space")

            batch_count += 1
            if batch_count >= args.checkpoint:
                save_checkpoint(results, remaining, solved)
                elapsed = time.time() - start
                rate = solved / elapsed if elapsed > 0 else 0
                print(f"  [CP] {solved} solved, {len(remaining)} remaining, {rate:.1f}/s")
                batch_count = 0

    # Final save
    save_checkpoint(results, remaining, solved)
    elapsed = time.time() - start
    rate = solved / elapsed if elapsed > 0 else 0
    unsolved = [n for n in remaining if n not in results or results[n] is None]

    print(f"\n=== DONE ===")
    print(f"  Solved: {solved}")
    print(f"  Unsolved: {len(unsolved)}")
    print(f"  Time: {elapsed:.1f}s ({rate:.1f} solves/s)")

    if unsolved:
        print(f"  Unsaved to {CHECKPOINT_FILE}")

    # Write final results
    final_path = Path("sieve_results.json")
    with open(final_path, "w") as f:
        json.dump({
            "solved": solved,
            "results": {str(k): list(v) if v else None for k, v in results.items()},
            "unsolved": unsolved,
            "elapsed": elapsed,
        }, f, indent=2)
    print(f"  Results saved to {final_path}")


if __name__ == "__main__":
    main()
