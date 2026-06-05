"""Convert SQLite solutions to JSONL for Kaggle dataset publish."""
import sqlite3, json, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
db_path = BASE / "erdos_solutions.db"
out_path = BASE / "kaggle_dataset" / "erdos_solutions.jsonl"
out_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

total = conn.execute('SELECT COUNT(*) FROM solutions').fetchone()[0]
batch_size = 10000

with open(out_path, 'w') as f:
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
print(f'File size: {os.path.getsize(out_path)/1024/1024:.1f} MB')
