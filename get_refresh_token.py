"""
One-time script to get a Dropbox refresh token.
Run this locally once, then never again.

Usage:
    python get_refresh_token.py
"""
import os, pathlib, urllib.request, urllib.parse, json, webbrowser

def load_env():
    env_path = pathlib.Path(__file__).parent / ".env"
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().lstrip("﻿"))

load_env()

APP_KEY    = os.environ.get("DROPBOX_APP_KEY", "").strip()
APP_SECRET = os.environ.get("DROPBOX_APP_SECRET", "").strip()

if not APP_KEY or not APP_SECRET:
    raise SystemExit("ERROR: DROPBOX_APP_KEY and DROPBOX_APP_SECRET must be set in .env")

# Step 1: open auth URL
auth_url = (
    "https://www.dropbox.com/oauth2/authorize"
    f"?client_id={APP_KEY}"
    "&token_access_type=offline"
    "&response_type=code"
)
print(f"\nOpening browser to authorise. If it doesn't open, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

code = input("Paste the authorisation code from Dropbox here: ").strip()

# Step 2: exchange code for refresh token
data = urllib.parse.urlencode({
    "code": code,
    "grant_type": "authorization_code",
    "client_id": APP_KEY,
    "client_secret": APP_SECRET,
}).encode()

req = urllib.request.Request("https://api.dropbox.com/oauth2/token", data=data)
with urllib.request.urlopen(req) as r:
    resp = json.loads(r.read())

refresh_token = resp.get("refresh_token")
if not refresh_token:
    raise SystemExit(f"ERROR: no refresh token in response: {resp}")

# Step 3: save to .env
env_path = pathlib.Path(__file__).parent / ".env"
lines = env_path.read_text(encoding="utf-8-sig").splitlines()
# remove old token lines, add refresh token
new_lines = [l for l in lines if not l.startswith("DROPBOX_TOKEN=") and not l.startswith("DROPBOX_REFRESH_TOKEN=")]
new_lines.append(f"DROPBOX_REFRESH_TOKEN={refresh_token}")
env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("\nDone! Refresh token saved to .env")
print("Now run: python update_secrets.py")
