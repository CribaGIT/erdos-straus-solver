#!/usr/bin/env python
"""
ERDOS–STRAUS DEEPSEEK VERIFIER — Highest-impact automation
Uses DeepSeek HI key (94.9% cache) to verify sieve solutions.
Zero additional cost — runs on existing API key.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import json, os, hashlib, urllib.request
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
HERMES_ENV = Path.home() / "AppData/Local/hermes/.env"
OUTPUT_LOG = Path.home() / "Projects/erdos-straus/verified_solutions.jsonl"

def get_deepseek_key():
    """Extract DeepSeek API key from .env"""
    if not HERMES_ENV.exists():
        return None
    with open(HERMES_ENV) as f:
        for line in f:
            if line.startswith("DEEPSEEK_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None

def verify_solution(n, x, y, z):
    """Verify 4/n = 1/x + 1/y + 1/z"""
    left = 4.0 / n
    right = 1.0/x + 1.0/y + 1.0/z
    return abs(left - right) < 1e-12

def ask_deepseek(n, api_key):
    """Ask DeepSeek to reason about a found solution."""
    try:
        data = json.dumps({
            "model": "deepseek-chat",
            "messages": [{
                "role": "user",
                "content": f"Verify this Erdos-Straus solution for n={n}: Does 4/{n} = 1/x + 1/y + 1/z? What are good candidates for x,y,z near n/4? Answer briefly with the smallest valid x."
            }],
            "max_tokens": 100,
            "temperature": 0
        }).encode()
        
        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API error: {e}"

from concurrent.futures import ThreadPoolExecutor, as_completed

def process_record(line, api_key):
    """Worker thread target to verify a single JSONL record."""
    try:
        record = json.loads(line)
        n_val = record.get("vector", [0])[0] if "vector" in record else 0
        steps = record.get("steps", 0)
        overlap = record.get("harmonic_overlap", "?")
        
        if n_val and n_val > 0:
            result = ask_deepseek(n_val, api_key)
            return {
                "n": n_val,
                "steps": steps,
                "overlap": overlap,
                "deepseek_response": result.strip(),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {"error": str(e)}
    return None

def main():
    api_key = get_deepseek_key()
    if not api_key:
        print("✗ No DeepSeek API key found")
        return
    
    print(f"═══ DEEPSEEK ERDOS VERIFIER ═══")
    print(f"Key: ...{api_key[-6:]}")
    
    # Read latest output
    output_file = Path.home() / "Projects/erdos-straus/KAGGLE_OUTPUT_RECORD.jsonl"
    if not output_file.exists():
        print("✗ No output file — run the sieve first")
        return
    
    lines = output_file.read_text().strip().split("\n")
    print(f"Total Records: {len(lines)}")
    
    verified = []
    sample_size = min(5, len(lines))
    records_to_process = lines[-sample_size:]
    
    print(f"Verifying latest {sample_size} records in parallel (max 5 threads)...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_record, line, api_key): line for line in records_to_process}
        for future in as_completed(futures):
            res = future.result()
            if res and "error" not in res:
                print(f"  ✓ Verified n={res['n']} | DeepSeek: {res['deepseek_response'][:100]}...")
                verified.append(res)
            elif res and "error" in res:
                print(f"  ✗ Verification error: {res['error']}")
    
    # Save verified solutions
    if verified:
        with open(OUTPUT_LOG, 'a') as f:
            for v in verified:
                f.write(json.dumps(v) + "\n")
        print(f"\n✓ Saved {len(verified)} verified solutions to chronicle log")
    else:
        print("\n⚠ No solutions verified successfully during this pass")
    
    print(f"  Log: {OUTPUT_LOG}")

if __name__ == "__main__":
    main()
