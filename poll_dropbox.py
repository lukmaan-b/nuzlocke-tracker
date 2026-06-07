"""
Download .sav files from a Dropbox folder, then re-run parse_saves.py.

Configuration (.env):
    DROPBOX_APP_KEY=xxx
    DROPBOX_APP_SECRET=xxx
    DROPBOX_REFRESH_TOKEN=xxx
    DROPBOX_SAVE_FOLDER=/pokemon-fire-red

Run manually:
    python poll_dropbox.py
"""
import os, sys, json, urllib.request, urllib.parse, urllib.error, subprocess, pathlib
from datetime import datetime, timezone

# ── load .env ──────────────────────────────────────────────────────────────────
def load_env():
    env_path = pathlib.Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    for key in ("DROPBOX_APP_KEY", "DROPBOX_APP_SECRET",
                "DROPBOX_REFRESH_TOKEN", "DROPBOX_SAVE_FOLDER"):
        if key in os.environ:
            os.environ[key] = os.environ[key].strip().lstrip("﻿")

load_env()

APP_KEY       = os.environ.get("DROPBOX_APP_KEY", "").strip()
APP_SECRET    = os.environ.get("DROPBOX_APP_SECRET", "").strip()
REFRESH_TOKEN = os.environ.get("DROPBOX_REFRESH_TOKEN", "").strip()
FOLDER        = os.environ.get("DROPBOX_SAVE_FOLDER", "/nuzlocke").strip()
SAVES_DIR     = pathlib.Path(__file__).parent / "saves"
SAVES_DIR.mkdir(exist_ok=True)

if not (APP_KEY and APP_SECRET and REFRESH_TOKEN):
    sys.exit("ERROR: DROPBOX_APP_KEY, DROPBOX_APP_SECRET and DROPBOX_REFRESH_TOKEN must be set.\n"
             "Run get_refresh_token.py first.")

# ── get a fresh short-lived access token from the refresh token ────────────────
def get_access_token():
    data = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id":     APP_KEY,
        "client_secret": APP_SECRET,
    }).encode()
    req = urllib.request.Request("https://api.dropbox.com/oauth2/token", data=data)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

TOKEN = get_access_token()

# ── Dropbox API helpers ────────────────────────────────────────────────────────
def dbx_post(endpoint, body):
    url = f"https://api.dropboxapi.com/2/{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def dbx_download(dropbox_path, dest_path):
    url = "https://content.dropboxapi.com/2/files/download"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
        },
    )
    with urllib.request.urlopen(req) as r:
        dest_path.write_bytes(r.read())

# ── main sync ─────────────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Polling Dropbox:{FOLDER} …")

    try:
        result = dbx_post("files/list_folder", {"path": FOLDER})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"Dropbox API error {e.code}: {body}")

    entries = result.get("entries", [])
    sav_files = [e for e in entries if e.get("name", "").lower().endswith((".sav", ".srm"))]

    if not sav_files:
        print(f"  No .sav files found in {FOLDER}")
        return

    # Names that should be in saves/ after this sync
    dropbox_names = {e["name"] for e in sav_files}

    # Remove any local saves that are NOT in Dropbox (stale/manual files)
    for local in list(SAVES_DIR.glob("*.sav")) + list(SAVES_DIR.glob("*.srm")):
        if local.name not in dropbox_names:
            print(f"  {local.name:20s} not in Dropbox — removing")
            local.unlink()

    updated = 0
    for entry in sav_files:
        name    = entry["name"]
        db_path = entry["path_lower"]
        db_mtime = entry.get("server_modified", "")
        dest    = SAVES_DIR / name

        # skip if local file is already up-to-date
        if dest.exists() and db_mtime:
            local_mtime = datetime.fromtimestamp(dest.stat().st_mtime, tz=timezone.utc)
            remote_mtime = datetime.fromisoformat(db_mtime.replace("Z", "+00:00"))
            if local_mtime >= remote_mtime:
                print(f"  {name:20s} up to date, skipping")
                continue

        print(f"  {name:20s} downloading …", end=" ")
        try:
            dbx_download(db_path, dest)
            print("OK")
            updated += 1
        except urllib.error.HTTPError as e:
            print(f"FAILED ({e.code})")

    if updated:
        print(f"\n  {updated} file(s) updated — regenerating data.json …")
        script = pathlib.Path(__file__).parent / "parse_saves.py"
        subprocess.run([sys.executable, str(script)], check=True)
    else:
        print("  All files up to date — nothing to do.")

if __name__ == "__main__":
    main()
