"""
Push .env values to GitHub Actions secrets.
Run after get_refresh_token.py.

Usage:
    python update_secrets.py
"""
import os, pathlib, subprocess, sys

def load_env():
    env_path = pathlib.Path(__file__).parent / ".env"
    vals = {}
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().lstrip("﻿")
    return vals

env = load_env()
gh = r"C:\Program Files\GitHub CLI\gh.exe"
repo = "lukmaan-b/nuzlocke-tracker"

secrets = {
    "DROPBOX_APP_KEY":      env.get("DROPBOX_APP_KEY"),
    "DROPBOX_APP_SECRET":   env.get("DROPBOX_APP_SECRET"),
    "DROPBOX_REFRESH_TOKEN":env.get("DROPBOX_REFRESH_TOKEN"),
    "DROPBOX_SAVE_FOLDER":  env.get("DROPBOX_SAVE_FOLDER"),
}

for name, value in secrets.items():
    if not value:
        print(f"  SKIP {name} (not in .env)")
        continue
    result = subprocess.run(
        [gh, "secret", "set", name, "--repo", repo],
        input=value, text=True, capture_output=True
    )
    if result.returncode == 0:
        print(f"  OK   {name}")
    else:
        print(f"  FAIL {name}: {result.stderr.strip()}")

# Remove old DROPBOX_TOKEN secret if it exists
subprocess.run([gh, "secret", "delete", "DROPBOX_TOKEN", "--repo", repo],
               capture_output=True)
print("  DEL  DROPBOX_TOKEN (no longer needed)")
