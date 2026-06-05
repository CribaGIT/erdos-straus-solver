"""Convert SQLite or local JSONL solutions to a subset JSONL for Kaggle dataset publish."""
import sqlite3, json, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
db_path = BASE / "erdos_solutions.db"
jsonl_source = BASE / "KAGGLE_OUTPUT_RECORD.jsonl"
out_path = BASE / "kaggle_dataset" / "erdos_solutions.jsonl"
out_path.parent.mkdir(parents=True, exist_ok=True)

# First priority: check if we have KAGGLE_OUTPUT_RECORD.jsonl locally.
# Since the full JSONL is 30+ GB, we export a high-value sample (e.g., last 500,000 solutions)
# to keep the Kaggle dataset updated and responsive.
if jsonl_source.exists() and jsonl_source.stat().st_size > 0:
    print(f"Reading from local log: {jsonl_source.name}...")
    max_lines = 500_000
    
    # Read the last N lines efficiently
    lines = []
    try:
        with open(jsonl_source, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            buffer_size = 1024 * 1024  # 1MB buffer
            pos = file_size
            data = b""
            while pos > 0 and len(lines) <= max_lines + 1:
                to_read = min(buffer_size, pos)
                pos -= to_read
                f.seek(pos)
                chunk = f.read(to_read)
                data = chunk + data
                lines = data.split(b"\n")
                if len(lines) > max_lines + 1:
                    break
        
        # Write to target path
        valid_lines = [l.decode("utf-8").strip() for l in lines[-(max_lines+1):] if l.strip()]
        with open(out_path, "w", encoding="utf-8", newline="\n") as f_out:
            for line in valid_lines:
                f_out.write(line + "\n")
        print(f"Wrote {len(valid_lines):,} solutions from tail of JSONL to {out_path}")
        print(f"File size: {os.path.getsize(out_path)/1024/1024:.2f} MB")
        sys.exit(0)
    except Exception as e:
        print(f"Failed to tail JSONL: {e}. Falling back to default export.")

# Second priority: fall back to SQLite database if it exists and has solutions table
if db_path.exists() and os.path.getsize(db_path) > 0:
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        total = conn.execute('SELECT COUNT(*) FROM solutions').fetchone()[0]
        batch_size = 10000
        with open(out_path, 'w', encoding='utf-8') as f:
            offset = 0
            while offset < total:
                rows = conn.execute(
                    'SELECT n, mod9, mod24, depth, x, y, z, num_solutions, source_file, timestamp '
                    'FROM solutions ORDER BY n LIMIT ? OFFSET ?',
                    (batch_size, offset)
                ).fetchall()
                for row in rows:
                    d = dict(row)
                    d['triple'] = [d.pop('x'), d.pop('y'), d.pop('z')]
                    d['num_solutions'] = d.pop('num_solutions')
                    d['source_file'] = d.pop('source_file')
                    f.write(json.dumps(d) + '\n')
                offset += batch_size
                print(f'  Wrote {min(offset, total):,}/{total:,}', end='\r')
                sys.stdout.flush()
        conn.close()
        print(f'\nDone: {total:,} solutions → {out_path}')
        print(f'File size: {os.path.getsize(out_path)/1024/1024:.2f} MB')
        sys.exit(0)
    except Exception as e:
        print(f"SQLite export failed: {e}")

# If nothing else works, create a dummy/empty file to prevent workflow crashes
print(f"No source data found. Writing empty file to {out_path}.")
out_path.write_text("")
