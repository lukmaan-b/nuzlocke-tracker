"""Location table for the Johto (HG/SS-in-Emerald) romhack.

Unlike the Kanto FRLG game, we don't have a decomp-generated map-name table for
this romhack, so we can't turn a raw mapGroup.mapNum into a place name
automatically. Instead:

  * AREA_COORDS holds the on-map position of every named Johto location. These
    are pre-calibrated against docs/assets/johto-map.png (1507x1056) as PERCENT
    positions (0-100), so they're resolution-independent.

  * MAP_TO_AREA maps the romhack's raw "mapGroup.mapNum" to one of those area
    names. It starts mostly empty and is filled in as players explore: every
    unmapped group.num is logged by parse_saves.py, so you can look up where a
    player actually was and add a line here.
"""

# Named Johto locations -> (x%, y%) on the Johto map image.
AREA_COORDS = {
    "New Bark Town":   (70.8, 67.4),
    "Cherrygrove City":(57.2, 67.4),
    "Violet City":     (47.9, 46.2),
    "Azalea Town":     (38.2, 84.1),
    "Goldenrod City":  (33.0, 66.3),
    "Ecruteak City":   (39.3, 29.1),
    "Olivine City":    (22.9, 48.5),
    "Cianwood City":   (11.4, 65.3),
    "Mahogany Town":   (52.6, 29.1),
    "Blackthorn City": (68.8, 29.1),
    "Indigo Plateau":  (90.7, 15.3),
    "Lake of Rage":    (52.0, 10.0),
}

# Romhack raw "mapGroup.mapNum" -> area name (see module docstring).
# Fill these in as group.num values are identified during play.
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
