"""
Download .sav files from a Dropbox folder, then re-run parse_saves.py.

Configuration: create a .env file next to this script:
    DROPBOX_TOKEN=sl.u.XXXX...
    DROPBOX_SAVE_FOLDER=/nuzlocke

Run manually:
    python poll_dropbox.py

Or schedule daily with Windows Task Scheduler (see README).
"""
import os, sys, json, urllib.request, urllib.error, subprocess, pathlib
from datetime import datetime, timezone

# ── load .env ──────────────────────────────────────────────────────────────────
def load_env():
    env_path = pathlib.Path(__file__).parent / ".env"
    if not env_path.exists():
        sys.exit(
            "ERROR: .env file not found.\n"
            "Copy .env.example to .env and fill in your DROPBOX_TOKEN and DROPBOX_SAVE_FOLDER."
        )
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

load_env()

TOKEN  = os.environ.get("DROPBOX_TOKEN", "").strip()
FOLDER = os.environ.get("DROPBOX_SAVE_FOLDER", "/nuzlocke").strip()
SAVES_DIR = pathlib.Path(__file__).parent / "saves"
SAVES_DIR.mkdir(exist_ok=True)

if not TOKEN:
    sys.exit("ERROR: DROPBOX_TOKEN not set in .env")

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
    arg = json.dumps({"path": dropbox_path})
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Dropbox-API-Arg": arg,
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
