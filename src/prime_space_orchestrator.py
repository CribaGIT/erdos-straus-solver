"""
Prime-space orchestrator for 4/n = 1/x + 1/y + 1/z verification.
GOVERNOR: consumed by erdos_straus_solver and CLI entrypoints.
"""
from __future__ import annotations
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass(frozen=True)
class Solution:
    n: int
    x: int
    y: int
    z: int

def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a

def _verify_chunk(start: int, end: int, out: mp.Queue) -> int:
    found = 0
    for n in range(start, end):
        if n <= 1:
            continue
        x_lo = n // 4 + 1
        x_hi = n * 2
        solved = False
        for x in range(x_lo, x_hi + 1):
            num = n * x
            denom = 4 * x - n
            if denom <= 0:
                continue
            if num % denom != 0:
                continue
            y = num // denom
            lhs = 4.0 / n - 1.0 / x - 1.0 / y
            if lhs <= 0:
                continue
            z = int(round(1.0 / lhs))
            if z > 0 and abs(1.0 / z - lhs) < 1e-9:
                out.put(Solution(n, x, y, z))
                found += 1
                solved = True
                break
        if not solved:
            out.put(Solution(n, 0, 0, 0))
    return found

class PrimeSpaceOrchestrator:
    def __init__(self, max_cores: int | None = None) -> None:
        self.cores = max_cores or max(1, mp.cpu_count() - 1)

    def execute(self, max_n: int, chunk_size: int = 50_000) -> List[Solution]:
        manager = mp.Manager()
        q: mp.Queue = manager.Queue()
        jobs: List[mp.Process] = []
        for lo in range(2, max_n + 1, chunk_size):
            hi = min(lo + chunk_size - 1, max_n)
            p = mp.Process(target=_verify_chunk, args=(lo, hi, q), daemon=True)
            jobs.append(p)
            p.start()
            while sum(j.is_alive() for j in jobs) >= self.cores:
                time.sleep(0.01)
        for j in jobs:
            j.join()
        results: List[Solution] = []
        while not q.empty():
            results.append(q.get())
        return results
