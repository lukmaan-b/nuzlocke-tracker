"""
Parse a folder of Pokemon FireRed/LeafGreen .sav files into docs/data.json.

Usage:
    python parse_saves.py [saves_dir] [output_json]
Defaults:
    saves_dir   = ./saves
    output_json = ./docs/data.json
"""
import sys, os, json, struct, glob
import gen3data

SIG = 0x08012025
SLOT = 0xE000  # 14 sections * 0x1000

# Gen 3 text encoding (subset sufficient for names)
_CHARS = {0x00: " "}
for i, c in enumerate("0123456789"): _CHARS[0xA1 + i] = c
for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"): _CHARS[0xBB + i] = c
for i, c in enumerate("abcdefghijklmnopqrstuvwxyz"): _CHARS[0xD5 + i] = c
_CHARS.update({0xAD: ".", 0xAE: "-", 0xB8: ",", 0xBA: "/",
               0xB0: "..", 0x2D: " ", 0x1B: "e", 0x2B: "e"})

def decode_str(b):
    out = []
    for x in b:
        if x == 0xFF:
            break
        out.append(_CHARS.get(x, ""))
    return "".join(out).strip()

# Substructure orderings keyed by PID % 24
_ORDERS = ['GAEM','GAME','GEAM','GEMA','GMAE','GMEA','AGEM','AGME','AEGM','AEMG',
           'AMGE','AMEG','EGAM','EGMA','EAGM','EAMG','EMGA','EMAG','MGAE','MGEA',
           'MAGE','MAEG','MEGA','MEAG']


def live_sections(data):
    """Return {section_id: file_offset} for the most recently saved slot."""
    best = None
    for s in range(2):
        base = s * SLOT
        secs, mx, valid = {}, -1, 0
        for i in range(14):
            soff = base + i * 0x1000
            if struct.unpack_from("<I", data, soff + 0xFF8)[0] == SIG:
                sid = struct.unpack_from("<H", data, soff + 0xFF4)[0]
                idx = struct.unpack_from("<I", data, soff + 0xFFC)[0]
                secs[sid] = soff
                valid += 1
                if idx != 0xFFFFFFFF:
                    mx = max(mx, idx)
        if valid == 14 and (best is None or mx > best[1]):
            best = (secs, mx)
    if best is None:
        raise ValueError("no valid save slot found")
    return best[0]


def reconstruct(data, secs, ids, per=0xF80):
    return b"".join(data[secs[i]:secs[i] + per] for i in ids)


def decode_mon(b, party_format, tid_full):
    """Decode an 80-byte (box) or 100-byte (party) Pokemon. Returns None if empty."""
    pid = struct.unpack_from("<I", b, 0)[0]
    otid = struct.unpack_from("<I", b, 4)[0]
    if pid == 0 and otid == 0:
        return None
    stored_chk = struct.unpack_from("<H", b, 0x1C)[0]
    key = pid ^ otid
    dec = bytearray(48)
    checksum = 0
    for i in range(12):
        w = struct.unpack_from("<I", b, 0x20 + i * 4)[0] ^ key
        struct.pack_into("<I", dec, i * 4, w)
    for i in range(24):
        checksum = (checksum + struct.unpack_from("<H", dec, i * 2)[0]) & 0xFFFF
    if checksum != stored_chk:
        return None  # not a real Pokemon (empty slot / garbage)

    order = _ORDERS[pid % 24]
    subs = {order[i]: dec[i * 12:(i + 1) * 12] for i in range(4)}
    G, M = subs['G'], subs['M']
    species = struct.unpack_from("<H", G, 0)[0]
    held = struct.unpack_from("<H", G, 2)[0]
    exp = struct.unpack_from("<I", G, 4)[0]
    misc = struct.unpack_from("<I", M, 4)[0]
    is_egg = (misc >> 30) & 1
    if species == 0 or species > 500:   # 500 = safe upper bound; real mons are 1-386
        return None

    nick = decode_str(b[8:18])
    ot = decode_str(b[0x14:0x1B])

    # shiny: (TIDlo ^ TIDhi ^ PIDlo ^ PIDhi) < 8
    pidlo, pidhi = pid & 0xFFFF, (pid >> 16) & 0xFFFF
    tidlo, tidhi = tid_full & 0xFFFF, (tid_full >> 16) & 0xFFFF
    shiny = (tidlo ^ tidhi ^ pidlo ^ pidhi) < 8

    mon = {
        "species": gen3data.species_name(species),
        "dex": gen3data.species_dex(species),
        "nickname": nick,
        "shiny": bool(shiny),
        "isEgg": bool(is_egg),
        "heldItem": held or None,
        "exp": exp,
    }
    if party_format:
        mon["level"] = b[0x54]
        mon["hp"] = struct.unpack_from("<H", b, 0x56)[0]
        mon["maxHp"] = struct.unpack_from("<H", b, 0x58)[0]
    return mon


def parse_save(path):
    with open(path, "rb") as f:
        data = f.read()
    secs = live_sections(data)

    # --- Section 0: trainer info (SaveBlock2) ---
    s0 = secs[0]
    name = decode_str(data[s0:s0 + 8])
    gender = "F" if data[s0 + 0x08] else "M"
    tid_full = struct.unpack_from("<I", data, s0 + 0x0A)[0]
    play_h = struct.unpack_from("<H", data, s0 + 0x0E)[0]
    play_m = data[s0 + 0x10]
    play_s = data[s0 + 0x11]

    # --- SaveBlock1: sections 1-4 (party, location, badge flags) ---
    SB1 = reconstruct(data, secs, (1, 2, 3, 4))
    px, py = struct.unpack_from("<H", SB1, 0)[0], struct.unpack_from("<H", SB1, 2)[0]
    map_group, map_num = SB1[4], SB1[5]
    location = gen3data.lookup_location(map_group, map_num)
    location.update({"mapGroup": map_group, "mapNum": map_num})

    # badges: flags array @0x0EE0, FLAG_BADGE01_GET = 0x820
    flags_base, badge0 = 0x0EE0, 0x820
    badge_list = []
    for i in range(8):
        f = badge0 + i
        bit = (SB1[flags_base + (f >> 3)] >> (f & 7)) & 1
        badge_list.append(bool(bit))

    # party
    party = []
    count = struct.unpack_from("<I", SB1, 0x34)[0]
    if 0 < count <= 6:
        for i in range(count):
            mon = decode_mon(SB1[0x38 + i * 100:0x38 + (i + 1) * 100], True, tid_full)
            if mon:
                party.append(mon)

    # --- FRLG+ Nuzlocke dead flags (SB1 offset 0x0a9e, 53 bytes, 1 bit per box slot) ---
    # Bit index = box*30 + slot; set = permanently fainted in Nuzlocke mode.
    # Only present in FRLG+; vanilla saves will just have zeros here (no harm).
    DEAD_FLAGS_OFF = 0x0a9e
    dead_flags = SB1[DEAD_FLAGS_OFF:DEAD_FLAGS_OFF + 53]

    def is_dead(flat_idx):
        return bool((dead_flags[flat_idx >> 3] >> (flat_idx & 7)) & 1)

    # --- PC boxes: sections 5-13 ---
    PC = reconstruct(data, secs, (5, 6, 7, 8, 9, 10, 11, 12, 13))
    boxes = [[] for _ in range(14)]
    base = 4  # u32 currentBox precedes the box data
    for b in range(14):
        for s in range(30):
            flat_idx = b * 30 + s
            off = base + flat_idx * 80
            mon = decode_mon(PC[off:off + 80], False, tid_full)
            if mon:
                mon["box"] = b + 1
                mon["dead"] = is_dead(flat_idx)
                boxes[b].append(mon)
    box_flat = [m for box in boxes for m in box]

    return {
        "id": os.path.splitext(os.path.basename(path))[0],
        "trainer": name,
        "gender": gender,
        "trainerId": tid_full & 0xFFFF,
        "playTime": {"h": play_h, "m": play_m, "s": play_s},
        "badges": sum(badge_list),
        "badgeList": badge_list,
        "location": location,
        "party": party,
        "boxes": box_flat,
        "boxCount": len(box_flat),
    }


def main():
    saves_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "saves")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "docs", "data.json")
    files = sorted(
        glob.glob(os.path.join(saves_dir, "*.sav")) +
        glob.glob(os.path.join(saves_dir, "*.srm"))
    )
    players = []
    for path in files:
        try:
            p = parse_save(path)
            players.append(p)
            loc = p["location"]
            note = "" if loc["known"] else "  [!] unmapped location, add to gen3data.LOCATIONS"
            print(f"  {p['id']:12s} '{p['trainer']}'  badges={p['badges']}  "
                  f"party={len(p['party'])}  box={p['boxCount']}  "
                  f"@ {loc['area']} (g{loc['mapGroup']}.{loc['mapNum']}){note}")
        except Exception as e:
            print(f"  [ERROR] {path}: {e}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"players": players}, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(players)} player(s) -> {out}")


if __name__ == "__main__":
    main()
