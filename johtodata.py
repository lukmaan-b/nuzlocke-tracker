"""Location table for the Johto (HG/SS-in-Emerald) romhack.

The map image (docs/assets/johto-map.png, 1434x872) is the actual in-game Town
Map, ripped from a screenshot with the player icon / cursor / UI removed. Its
red/blue squares are the in-game city markers.

We don't have a decomp map-name table for this romhack, so we can't turn a raw
mapGroup.mapNum into a place name automatically. Instead:

  * AREA_COORDS holds the on-map position of named Johto locations as PERCENT
    positions (0-100), calibrated against the in-game map image. It's filled in
    as towns are identified (the in-game markers are unlabeled).

  * MAP_TO_AREA maps the romhack's raw "mapGroup.mapNum" to one of those area
    names. Every unmapped group.num is logged by parse_saves.py, so you can look
    up where a player actually was and add a line here.
"""

# Named Johto locations -> (x%, y%) on the in-game Johto map image.
# Calibrated against docs/assets/johto-map.png by matching the in-game city
# markers to Johto geography. The markers are unlabeled in-game, so all of these
# except Violet City are APPROXIMATE best-guesses and should be corrected as
# players visit each town (the parser logs each unmapped group.num).
#
# NOTE: this is the *Johto* map only. This romhack is HG/SS-based and has a Kanto
# post-game section (badges 9-16, Indigo Plateau / Mt. Silver) that is NOT yet
# tracked — no Kanto map asset and badge handling assumes 8 Johto badges. See
# README "Known limitations".
AREA_COORDS = {
    "Violet City":      (44.8, 35.0),   # CONFIRMED (WES, outside Sprout Tower)
    # --- approximate (unlabeled in-game markers, matched by geography) ---
    "New Bark Town":    (68.5, 68.8),
    "Cherrygrove City": (51.7, 68.3),
    "Azalea Town":      (38.6, 85.2),
    "Goldenrod City":   (31.6, 60.0),
    "Ecruteak City":    (25.0, 35.6),
    "Olivine City":     (18.3, 73.9),
    "Cianwood City":    (11.9, 63.3),
    "Mahogany Town":    (71.9, 41.4),
    "Blackthorn City":  (84.8, 32.7),
    "Lake of Rage":     (55.2, 14.1),
}

# Romhack raw "mapGroup.mapNum" -> area name (see module docstring).
MAP_TO_AREA = {
    "3.0": "Violet City",   # confirmed: outside Sprout Tower
}


def lookup_location(group, num):
    area = MAP_TO_AREA.get(f"{group}.{num}")
    xy = AREA_COORDS.get(area) if area else None
    if not xy:
        return {"area": area or "Unknown", "x": 50.0, "y": 50.0,
                "known": False}
    return {"area": area, "x": float(xy[0]), "y": float(xy[1]), "known": True}
