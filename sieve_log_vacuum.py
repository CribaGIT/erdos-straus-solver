#!/usr/bin/env python3
"""
Sieve Log Vacuum Utility
Parses KAGGLE_OUTPUT_RECORD.jsonl, populates erdos_solutions.db,
and truncates the log file to release disk space while preserving tail history.
"""
import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
db_path = BASE / "erdos_solutions.db"
jsonl_path = BASE / "KAGGLE_OUTPUT_RECORD.jsonl"
temp_jsonl_path = BASE / "KAGGLE_OUTPUT_RECORD.jsonl.tmp"

TAIL_COUNT = 50_000  # Number of trailing lines to keep in the JSONL log
BATCH_SIZE = 50_000

def init_db():
    print(f"[+] Initializing database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solutions (
            n INTEGER PRIMARY KEY,
            mod9 INTEGER,
            mod24 INTEGER,
            depth TEXT,
            x INTEGER,
            y INTEGER,
            z INTEGER,
            num_solutions INTEGER,
            source_file TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def vacuum():
    if not jsonl_path.exists():
        print(f"[-] Log file {jsonl_path} does not exist. Aborting.")
        return

    file_size_gb = jsonl_path.stat().st_size / (1024 ** 3)
    print(f"[+] Found log file: {jsonl_path.name} ({file_size_gb:.2f} GB)")

    init_db()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("[+] Importing log entries into SQLite solutions table...")
    
    count = 0
    batch = []
    
    # We will also keep the last TAIL_COUNT lines to write back to the JSONL log
    # To do this memory-efficiently, we can do a two-pass approach or just use a circular buffer for the tail.
    from collections import deque
    tail_buffer = deque(maxlen=TAIL_COUNT)

    with open(jsonl_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            tail_buffer.append(line)
            
            try:
                data = json.loads(line)
                n = data.get("n")
                if n is None:
                    continue
                
                triple = data.get("triple", [0, 0, 0])
                # Handle possible missing elements in triple
                while len(triple) < 3:
                    triple.append(0)

                batch.append((
                    n,
                    data.get("mod9", n % 9),
                    data.get("mod24", n % 24),
                    data.get("depth", "BREACH_MOD9"),
                    triple[0],
                    triple[1],
                    triple[2],
                    data.get("num_solutions", 0),
                    data.get("source_file", "kaggle_t4"),
                    data.get("timestamp", datetime.now().isoformat())
                ))

                if len(batch) >= BATCH_SIZE:
                    cursor.executemany("""
                        INSERT OR REPLACE INTO solutions (n, mod9, mod24, depth, x, y, z, num_solutions, source_file, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    conn.commit()
                    count += len(batch)
                    print(f"  Processed {count:,} solutions...", end="\r")
                    batch = []
            except Exception as e:
                # Skip corrupt lines
                pass

    if batch:
        cursor.executemany("""
            INSERT OR REPLACE INTO solutions (n, mod9, mod24, depth, x, y, z, num_solutions, source_file, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        count += len(batch)

    print(f"\n[+] Successfully imported {count:,} solutions to erdos_solutions.db.")
    
    # Get total solutions count in DB
    cursor.execute("SELECT COUNT(*) FROM solutions")
    db_count = cursor.fetchone()[0]
    print(f"[+] Database count: {db_count:,} solutions.")
    
    conn.close()

    # Now write the trailing lines to the truncated JSONL file
    print(f"[+] Truncating JSONL log file, keeping the last {len(tail_buffer):,} lines...")
    with open(temp_jsonl_path, "w", encoding="utf-8", newline="\n") as f_out:
        for line in tail_buffer:
            f_out.write(line + "\n")

    # Replace the old log file with the truncated one
    try:
        os.remove(jsonl_path)
        os.rename(temp_jsonl_path, jsonl_path)
        new_size_mb = jsonl_path.stat().st_size / (1024 * 1024)
        print(f"[+] Log truncation complete. New file size: {new_size_mb:.2f} MB")
        print(f"[+] Released approx. {file_size_gb:.2f} GB of disk space.")
    except Exception as e:
        print(f"[-] Error replacing log file: {e}")
        if temp_jsonl_path.exists():
            print(f"[!] Truncated copy remains at: {temp_jsonl_path.name}")

if __name__ == "__main__":
    vacuum()
