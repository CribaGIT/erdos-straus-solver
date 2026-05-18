#!/usr/bin/env python
"""
ERDOS–STRAUS PROGRESSION SYSTEM
Multi-node progress tracking with terminal + HTML dashboard
DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, os, time, math
from datetime import datetime
from pathlib import Path
from atomic_writer import safe_read

BASE = Path.home() / "Projects/erdos-straus"
MANIFEST = BASE / "work_manifest.json"
OUTPUT = BASE / "KAGGLE_OUTPUT_RECORD.jsonl"

# ═══════════════════════════════════════════════════════
# 1. READ STATE — Pull data from manifest + output log
# ═══════════════════════════════════════════════════════

def load_manifest():
    if MANIFEST.exists():
        with open(MANIFEST) as f:
            return json.load(f)
    return None

def count_output():
    lines = safe_read()
    total = len(lines)
    stable = sum(1 for l in lines if '"harmonic_overlap":"STABLE"' in l)
    breach = sum(1 for l in lines if '"harmonic_overlap":"BREACH"' in l)
    return total, stable, breach

# ═══════════════════════════════════════════════════════
# 2. TERMINAL PROGRESS BAR
# ═══════════════════════════════════════════════════════

def terminal_bar(label, current, total, width=40, color="white"):
    pct = min(100, (current / total) * 100) if total > 0 else 0
    filled = int(width * pct / 100)
    empty = width - filled
    
    bars = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    
    full_blocks = filled // 8
    remainder = filled % 8
    
    bar = "█" * full_blocks
    if remainder > 0: bar += bars[remainder]
    bar += "░" * empty
    
    color_codes = {
        "green":  "\033[92m", "yellow": "\033[93m",
        "red":    "\033[91m", "blue":   "\033[94m",
        "cyan":   "\033[96m", "white":  "\033[97m",
        "reset":  "\033[0m"
    }
    
    c = color_codes.get(color, "")
    r = color_codes["reset"]
    
    return f"{label:>20} {c}{bar}{r} {pct:5.1f}%  ({current:>15,} / {total:>15,})"

def terminal_dashboard():
    m = load_manifest()
    total_sols, stable, breach = count_output()
    
    if not m:
        print("No manifest found. Run sieve first.")
        return
    
    target = m["total_range"]
    current = m["current_progress"]
    overall_pct = (current / target) * 100 if target > 0 else 0
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        ERDOS–STRAUS SIEVE — PROGRESSION DASHBOARD          ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"║  Target: {target:>20,}  │  Progress: {overall_pct:.6f}%          ║")
    print(f"║  Solutions: {total_sols:>17,}  │  STABLE: {stable:<6} BREACH: {breach:<6} ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Overall progress
    print(terminal_bar("OVERALL", current, target, 50, "cyan"))
    print()
    
    # Per-node progress
    if "nodes" in m:
        print("═══ NODE PROGRESS ═══")
        for name, node in m["nodes"].items():
            chunks_per = node.get("chunks_per_run", 1)
            last_chunk = node.get("last_chunk", 0) or 0
            sols = node.get("total_solutions", 0) or 0
            status = node.get("status", "unknown")
            
            icon = "✅" if status == "active" else "⚠️" if status == "manual" else "💤"
            print(f"  {icon} {name:>20}: chunk_at {last_chunk:>15,} | {sols:>8,} sols | {status}")
    
    print()
    print("═══ SOLUTION DISTRIBUTION ═══")
    if total_sols > 0:
        stable_bar_width = int(40 * stable / total_sols)
        breach_bar_width = int(40 * breach / total_sols)
        void = 40 - stable_bar_width - breach_bar_width
        print(f"  STABLE: {'█' * stable_bar_width}{'░' * (40 - stable_bar_width)} {stable} ({stable/total_sols*100:.1f}%)")
        print(f"  BREACH: {'█' * breach_bar_width}{'░' * (40 - breach_bar_width)} {breach} ({breach/total_sols*100:.1f}%)")

# ═══════════════════════════════════════════════════════
# 3. HTML PROGRESS DASHBOARD
# ═══════════════════════════════════════════════════════

def html_dashboard():
    m = load_manifest()
    total_sols, stable, breach = count_output()
    if not m: return "<h1>No manifest</h1>"
    
    target = m["total_range"]
    current = m["current_progress"]
    overall_pct = (current / target) * 100 if target > 0 else 0
    
    def bar(label, cur, tot, color="#88aacc"):
        p = min(100, (cur/tot)*100) if tot>0 else 0
        return '<div style="margin:4px 0"><div style="display:flex;justify-content:space-between;font-size:10px;color:#557799"><span>'+label+'</span><span>'+str(round(p,4))+'%  ('+str(cur)+' / '+str(tot)+')</span></div><div style="background:#1a1f24;height:14px;border-radius:3px;overflow:hidden;border:1px solid #334466"><div style="background:'+color+';height:100%;width:'+str(p)+'%;transition:width 1s;border-radius:2px"></div></div></div>'
    
    node_html = ""
    for name, node in m.get("nodes", {}).items():
        st = node.get("status","dormant")
        lc = str(node.get("last_chunk",0) or 0)
        so = str(node.get("total_solutions",0) or 0)
        cr = str(node.get("chunks_per_run",0) or 0)
        node_html += '<div class="card node '+st+'"><div class="node-name">'+name+'</div><div class="node-stat">Chunk: '+lc+'</div><div class="node-stat">Sols: '+so+'</div><div class="node-stat">Per run: '+cr+'</div></div>'
    
    stable_bar = bar("STABLE", stable, total_sols if total_sols>0 else 1, "#44aa44")
    breach_bar = bar("BREACH", breach, total_sols if total_sols>0 else 1, "#aa8844")
    overall_bar = bar("OVERALL", current, target, "#44aacc")
    ts = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
    axiom = m.get("axiom","?")
    version = m.get("version","?")
    
    return '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Erdos–Straus Progression</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0f18;color:#88aacc;font:11px Courier New,monospace;padding:20px;max-width:900px;margin:0 auto}
h1{color:#aaccee;font-size:14px;letter-spacing:2px;margin-bottom:20px}
h2{color:#6688aa;font-size:11px;letter-spacing:1px;margin:16px 0 8px}
.card{background:#0f1620;border:1px solid #224466;border-radius:4px;padding:12px;margin:8px 0}
.card h3{color:#aaccee;font-size:10px;letter-spacing:1px;margin-bottom:8px}
.stat{display:flex;justify-content:space-between;padding:2px 0;font-size:10px}
.stat .val{color:#aaccee;font-weight:bold}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px}
.node{padding:8px;border-radius:3px}
.node.active{border-left:3px solid #44aa44}
.node.manual{border-left:3px solid #aa8844}
.node.dormant{border-left:3px solid #444466}
.node-name{font-size:10px;color:#aaccee;margin-bottom:4px}
.node-stat{font-size:9px;color:#557799}
</style></head><body>
<h1>ERDOS–STRAUS PROGRESSION</h1>
<div class="card">
<div class="stat"><span>TARGET</span><span class="val">'''+str(target)+'''</span></div>
<div class="stat"><span>PROGRESS</span><span class="val">'''+str(round(overall_pct,6))+'''%</span></div>
<div class="stat"><span>SOLUTIONS</span><span class="val">'''+str(total_sols)+'''</span></div>
<div class="stat"><span>STABLE</span><span class="val" style="color:#88cc88">'''+str(stable)+'''</span></div>
<div class="stat"><span>BREACH</span><span class="val" style="color:#ff8844">'''+str(breach)+'''</span></div>
</div>
'''+overall_bar+'''
<h2>NODE STATUS</h2>
<div class="grid">'''+node_html+'''</div>
<h2>SOLUTION DISTRIBUTION</h2>
'''+stable_bar+breach_bar+'''
<div class="card" style="margin-top:20px">
<div class="node-stat">Axiom: '''+axiom+''' | Version: '''+version+'''</div>
<div class="node-stat">Updated: '''+ts+'''</div>
</div>
</body></html>'''

# ═══════════════════════════════════════════════════════
# 4. AUTO-UPDATE FUNCTION (call from cron)
# ═══════════════════════════════════════════════════════

def auto_update():
    """Called by cron to refresh the dashboard."""
    # Count latest output
    total, stable, breach = count_output()
    
    # Update manifest
    m = load_manifest()
    if m:
        m["solutions_total"] = total
        m["stable_regions"] = stable
        m["breach_regions"] = breach
        m["last_updated"] = datetime.now().isoformat()
        
        with open(MANIFEST, 'w') as f:
            json.dump(m, f, indent=2)
    
    # Generate HTML
    html = html_dashboard()
    html_path = BASE / "progression_dashboard.html"
    html_path.write_text(html)
    
    # Copy to G: drive
    gdrive = Path("G:/My Drive/Resonance_Archive/progression_dashboard.html")
    try:
        gdrive.write_text(html)
    except:
        pass
    
    print(f"✓ Dashboard updated: {total:,} solutions | STABLE:{stable} BREACH:{breach}")
    return total, stable, breach

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if "--auto" in sys.argv:
        auto_update()
    elif "--html" in sys.argv:
        html = html_dashboard()
        path = BASE / "progression_dashboard.html"
        path.write_text(html)
        print(f"✓ Saved to {path}")
    else:
        terminal_dashboard()
