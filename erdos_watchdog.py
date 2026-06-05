"""
ERDOS OUTPUT WATCHDOG — pulls notebook output, detects changes, bridges to Mirage.
Trigger: Windows scheduled task every 5 min.
Pull layer: kaggle kernels output (notebook persists /kaggle/working/ natively).
"""
import os
import json
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

NOTEBOOK_KERNELS = [
    'commencethescourge/erdos-hot-corridor-sieve',
    'commencethescourge/erdos-straus-solver',
]
PULL_DIR = Path(r'C:\Users\dasha\Projects\erdos-straus\kaggle_output')

WATCH_PATHS = [
    PULL_DIR / 'erdos-p100-notebook',
    PULL_DIR / 'erdos-t4-sieve',
    Path(r'C:\Users\dasha\ERDOS_OUTPUT_RECORD.jsonl'),
    PULL_DIR,
]

STATE_FILE = PULL_DIR / '.watchdog_state.json'
LOG_FILE = PULL_DIR / 'erdos_watchdog.log'

def hash_file(path):
    if not path.exists():
        return None
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def hash_dir(path):
    if not path.exists() or not path.is_dir():
        return None
    hashes = []
    for f in sorted(path.iterdir()):
        if f.is_file() and (f.name.startswith('.') or f.name == LOG_FILE.name or f.name == STATE_FILE.name):
            continue
        if f.is_file():
            hashes.append(hash_file(f))
    return hashlib.sha256(''.join(h for h in hashes if h).encode()).hexdigest()

def log(msg):
    ts = datetime.now().isoformat(timespec='seconds')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check():
    # ── PULL LAYER: download notebook output before hash detection ──
    _pull_notebook_output()

    state = load_state()
    changes = []

    for path in WATCH_PATHS:
        key = str(path)
        if path.is_dir():
            current = hash_dir(path)
        elif path.is_file():
            current = hash_file(path)
        else:
            current = None

        previous = state.get(key)

        if current is None and previous is None:
            continue
        elif current is None and previous is not None:
            changes.append(f"GONE: {key}")
        elif current is not None and previous is None:
            changes.append(f"NEW: {key}")
            if path.is_file():
                size = path.stat().st_size
                changes.append(f"  size: {size} bytes")
        elif current != previous:
            changes.append(f"CHANGED: {key}")
            if path.is_file():
                size = path.stat().st_size
                changes.append(f"  size: {size} bytes")

        state[key] = current

    if changes:
        log(f"DETECTED {len(changes)} change(s):")
        for c in changes:
            log(f"  {c}")

        # Push alert via Mirage WebSocket if available
        try:
            import asyncio
            import websockets

            async def push_alert():
                try:
                    async with websockets.connect('ws://localhost:8765') as ws:
                        await ws.send(json.dumps({
                            "type": "watchdog_alert",
                            "source": "erdos_output",
                            "changes": changes,
                            "timestamp": datetime.now().isoformat(),
                        }))
                except Exception:
                    pass

            asyncio.run(push_alert())
        except Exception:
            pass
    else:
        log("no changes")

    save_state(state)


def _pull_notebook_output():
    """Pull persisted notebook output from all kernels. Silent unless successful or unexpected error."""
    for kernel in NOTEBOOK_KERNELS:
        _pull_one(kernel)


def _pull_one(kernel):
    """Pull output from a single notebook kernel into a namespaced subdirectory."""
    out_dir = PULL_DIR / kernel.split('/')[-1]
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ['kaggle', 'kernels', 'output', kernel,
             '-p', str(out_dir), '--force'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            log(f"Pulled {kernel}")
        elif 'not found' in result.stderr.lower() or '403' in result.stderr:
            pass  # kernel not yet run or auth expired — expected
        else:
            log(f"Pull warning [{kernel}]: {result.stderr.strip()[-200:]}")
    except subprocess.TimeoutExpired:
        pass  # network hiccup — retry next cycle
    except Exception as e:
        log(f"Pull error [{kernel}]: {e}")


if __name__ == '__main__':
    check()
