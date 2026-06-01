"""Microtask 4: Generate dashboard JSON from existing SQLite data.

Produces: erdos_aggregates.json with:
  - mod24_mod9_heatmap: matrix[mod24][mod9] = {breach, stable, total}
  - node_contributions: source_file -> {solutions, breach, stable}
  - daily_totals: timestamp -> {solutions, breach, stable}
  - summary: {total_solutions, unique_n, breach_rate, last_updated}
"""

import sqlite3, json, os
from collections import defaultdict

erdos_dir = os.path.expanduser(r'~/Projects/erdos-straus')
db_path = os.path.join(erdos_dir, 'erdos_solutions.db')

conn = sqlite3.connect(db_path)

# --- mod24 × mod9 heatmap ---
rows = conn.execute("""
    SELECT mod24, mod9,
           COUNT(*) as total,
           SUM(CASE WHEN depth LIKE '%BREACH%' THEN 1 ELSE 0 END) as breach,
           SUM(CASE WHEN depth LIKE '%STABLE%' THEN 1 ELSE 0 END) as stable
    FROM solutions
    GROUP BY mod24, mod9
    ORDER BY mod24, mod9
""").fetchall()

heatmap = {}
for mod24, mod9, total, breach, stable in rows:
    key = f"{mod24}_{mod9}"
    heatmap[key] = {
        "mod24": mod24,
        "mod9": mod9,
        "total": total,
        "breach": breach,
        "stable": stable,
        "breach_rate": round(breach / total * 100, 1) if total > 0 else 0
    }

# --- Fill in zeros for all valid mod24 classes ---
valid_mod24 = [1, 5, 7, 9, 11, 13, 17, 19, 23]
valid_mod9 = list(range(9))
for m24 in valid_mod24:
    for m9 in valid_mod9:
        key = f"{m24}_{m9}"
        if key not in heatmap:
            heatmap[key] = {
                "mod24": m24, "mod9": m9,
                "total": 0, "breach": 0, "stable": 0, "breach_rate": 0
            }

# --- Node contributions ---
node_rows = conn.execute("""
    SELECT source_file,
           COUNT(*) as total,
           SUM(CASE WHEN depth LIKE '%BREACH%' THEN 1 ELSE 0 END) as breach,
           SUM(CASE WHEN depth LIKE '%STABLE%' THEN 1 ELSE 0 END) as stable,
           COUNT(DISTINCT n) as unique_n
    FROM solutions
    GROUP BY source_file
    ORDER BY total DESC
""").fetchall()

node_contributions = []
for src, total, breach, stable, unique_n in node_rows:
    node_contributions.append({
        "source": src,
        "solutions": total,
        "breach": breach,
        "stable": stable,
        "unique_n": unique_n,
        "breach_rate": round(breach / total * 100, 1) if total > 0 else 0
    })

# --- Depth distribution ---
depth_rows = conn.execute("""
    SELECT depth, COUNT(*) as count
    FROM solutions
    GROUP BY depth
    ORDER BY count DESC
""").fetchall()

depth_distribution = {row[0]: row[1] for row in depth_rows}

# --- Summary ---
total_sols = conn.execute("SELECT COUNT(*) FROM solutions").fetchone()[0]
unique_n = conn.execute("SELECT COUNT(DISTINCT n) FROM solutions").fetchone()[0]
total_breach = conn.execute("SELECT COUNT(*) FROM solutions WHERE depth LIKE '%BREACH%'").fetchone()[0]
total_stable = conn.execute("SELECT COUNT(*) FROM solutions WHERE depth LIKE '%STABLE%'").fetchone()[0]
max_n = conn.execute("SELECT MAX(n) FROM solutions").fetchone()[0]
min_n = conn.execute("SELECT MIN(n) FROM solutions").fetchone()[0]

summary = {
    "total_solutions": total_sols,
    "unique_n": unique_n,
    "breach": total_breach,
    "stable": total_stable,
    "breach_rate": round(total_breach / total_sols * 100, 1) if total_sols > 0 else 0,
    "n_range": [min_n, max_n],
    "last_updated": "2026-05-28",
    "work_manifest_solutions_claimed": 8335340,
    "coverage_pct": round(total_sols / 8335340 * 100, 1) if 8335340 > 0 else 0
}

aggregates = {
    "summary": summary,
    "mod24_mod9_heatmap": heatmap,
    "node_contributions": node_contributions,
    "depth_distribution": depth_distribution
}

output_path = os.path.join(erdos_dir, 'erdos_aggregates.json')
with open(output_path, 'w') as f:
    json.dump(aggregates, f, indent=2)

print(f"Dashboard JSON written: {output_path}")
print(f"  {total_sols:,} total solutions across {len(node_contributions)} nodes")
print(f"  {len(heatmap)} mod24×mod9 cells")
print(f"  {len(depth_distribution)} depth categories")
print(f"  Size: {os.path.getsize(output_path)/1024:.0f} KB")

conn.close()
