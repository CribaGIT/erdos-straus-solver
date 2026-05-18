#!/usr/bin/env python
"""
ERDOS ATOMIC WRITER — Prevents overlap between sieve writer and dashboard reader.
Windows-compatible: uses temp file + atomic rename (no fcntl needed).
"""
import os, json, time
from pathlib import Path

OUTPUT = Path.home() / "Projects/erdos-straus/KAGGLE_OUTPUT_RECORD.jsonl"
LOCK = Path.home() / "Projects/erdos-straus/.sieve.lock"

def acquire_lock(timeout=30):
    """Windows-compatible lock using temp file marker."""
    start = time.time()
    while time.time() - start < timeout:
        if not LOCK.exists():
            try:
                LOCK.write_text(str(os.getpid()))
                # Verify we got it (race condition check)
                time.sleep(0.1)
                if LOCK.read_text().strip() == str(os.getpid()):
                    return True
            except:
                pass
        time.sleep(0.5)
    return False

def release_lock():
    """Release the lock file."""
    try:
        if LOCK.exists() and LOCK.read_text().strip() == str(os.getpid()):
            LOCK.unlink()
    except:
        pass

def atomic_append(entry_json):
    """Thread-safe append to output log using atomic rename."""
    if not acquire_lock():
        print("⚠ Could not acquire lock — another process is writing")
        return False
    
    try:
        tmp = OUTPUT.with_suffix('.tmp')
        existing = OUTPUT.read_text() if OUTPUT.exists() else ""
        tmp.write_text(existing + entry_json + "\n")
        tmp.replace(OUTPUT)  # atomic on NTFS
        return True
    finally:
        release_lock()

def safe_read():
    """Read output safely with retry if locked."""
    for _ in range(5):
        if not LOCK.exists():
            if OUTPUT.exists():
                return OUTPUT.read_text().strip().split("\n")
            return []
        time.sleep(0.3)
    # Fallback: read anyway if lock is stale (>60s)
    if LOCK.exists():
        age = time.time() - LOCK.stat().st_mtime
        if age > 60:
            LOCK.unlink()  # break stale lock
    return OUTPUT.read_text().strip().split("\n") if OUTPUT.exists() else []

if __name__ == "__main__":
    # Test
    print("✓ Atomic writer ready")
    print(f"  Lock: {LOCK}")
    print(f"  Output: {OUTPUT}")
    lines = safe_read()
    print(f"  Current entries: {len(lines)}")
