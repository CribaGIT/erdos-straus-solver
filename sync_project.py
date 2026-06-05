#!/usr/bin/env python3
"""
MANIFOLD PROJECT SYNCHRONIZER
Automates linking issues and PRs across MANIFOLD repositories to the MANIFOLD Core Project Board.
"""
import os
import json
import subprocess
import sys

# Ensure GITHUB_TOKEN environment variable is cleared so gh CLI falls back to the valid keyring token
if "GITHUB_TOKEN" in os.environ:
    del os.environ["GITHUB_TOKEN"]

OWNER = "COMMENCINGTHESCOURGE"
PROJECT_NUMBER = 3
PROJECT_ID = "PVT_kwHOEGoPVc4BZx6r"

# Core repositories to sync
REPOS = [
    "erdos-straus-solver",
    "prompt-asset-marketplace",
    "prompt-asset-conductor",
    "trench-builder",
    "aetherion-continuum",
    "flux-chamber",
    "hyperpoly-terrain",
    "guinea-pig-trench-portal"
]

STATUS_TODO = "f75ad846"
STATUS_IN_PROGRESS = "47fc9ee4"
STATUS_DONE = "98236657"

def run_command(cmd):
    """Run shell command and return stdout as string."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd)}")
        print(f"Stderr: {e.stderr}")
        return None

def get_items(repo, item_type="issue"):
    """Get items from a repository using gh CLI."""
    cmd = ["gh", item_type, "list", "--repo", f"{OWNER}/{repo}", "--state", "all", "--limit", "20", "--json", "url,state,title"]
    output = run_command(cmd)
    if not output:
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []

def add_to_project(item_url):
    """Add an issue/PR to the project board and return the item ID."""
    cmd = ["gh", "project", "item-add", str(PROJECT_NUMBER), "--owner", OWNER, "--url", item_url, "--format", "json"]
    output = run_command(cmd)
    if not output:
        return None
    try:
        data = json.loads(output)
        return data.get("id")
    except json.JSONDecodeError:
        # Fallback if output format changes
        if "id" in output:
            for part in output.split():
                if part.startswith("id="):
                    return part.split("=")[1]
        return None

def set_item_status(item_id, status_id):
    """Set the Status field of a project item."""
    cmd = [
        "gh", "project", "item-edit",
        "--id", item_id,
        "--field-id", "PVTSSF_lAHOEGoPVc4BZx6rzhUuOwg",
        "--project-id", PROJECT_ID,
        "--single-select-option-id", status_id
    ]
    run_command(cmd)

def main():
    print(f"=== Starting MANIFOLD Project Sync (Project #{PROJECT_NUMBER}) ===")
    
    total_added = 0
    for repo in REPOS:
        print(f"\nScanning repository: {OWNER}/{repo}...")
        
        # Get issues and PRs
        issues = get_items(repo, "issue")
        prs = get_items(repo, "pr")
        items = issues + prs
        
        if not items:
            print("  No issues or PRs found.")
            continue
            
        print(f"  Found {len(items)} items to process.")
        for item in items:
            url = item.get("url")
            state = item.get("state", "").upper()
            title = item.get("title", "")
            
            # Map state to Project Status option ID
            if state == "OPEN":
                # Check if it looks in-progress or todo
                status_id = STATUS_TODO
            else:
                status_id = STATUS_DONE
                
            print(f"  Adding: {title[:50]}... ({state})")
            item_id = add_to_project(url)
            if item_id:
                set_item_status(item_id, status_id)
                total_added += 1
            else:
                print(f"    ⚠ Skipped/Already exists on board: {url}")
                
    print(f"\n=== Sync Complete! Added/Updated {total_added} items across {len(REPOS)} repositories. ===")

if __name__ == "__main__":
    main()
