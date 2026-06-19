"""Static lookup tables for Gen 3 (FireRed/LeafGreen) save parsing."""
import re
import mapdata    # auto-generated "group.num" -> in-game map name (Kanto)
import johtodata  # raw "group.num" -> Johto coords (HG/SS romhack)

# Internal species index -> name.
# For FR/LG, internal indices 1-251 are identical to the National Dex order,
# which covers every wild/obtainable species in a Kanto run.
_DEX = [
    "Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard",
    "Squirtle","Wartortle","Blastoise","Caterpie","Metapod","Butterfree",
    "Weedle","Kakuna","Beedrill","Pidgey","Pidgeotto","Pidgeot","Rattata",
    "Raticate","Spearow","Fearow","Ekans","Arbok","Pikachu","Raichu",
    "Sandshrew","Sandslash","Nidoran-F","Nidorina","Nidoqueen","Nidoran-M",
    "Nidorino","Nidoking","Clefairy","Clefable","Vulpix","Ninetales",
    "Jigglypuff","Wigglytuff","Zubat","Golbat","Oddish","Gloom","Vileplume",
    "Paras","Parasect","Venonat","Venomoth","Diglett","Dugtrio","Meowth",
    "Persian","Psyduck","Golduck","Mankey","Primeape","Growlithe","Arcanine",
    "Poliwag","Poliwhirl","Poliwrath","Abra","Kadabra","Alakazam","Machop",
    "Machoke","Machamp","Bellsprout","Weepinbell","Victreebel","Tentacool",
    "Tentacruel","Geodude","Graveler","Golem","Ponyta","Rapidash","Slowpoke",
    "Slowbro","Magnemite","Magneton","Farfetch'd","Doduo","Dodrio","Seel",
    "Dewgong","Grimer","Muk","Shellder","Cloyster","Gastly","Haunter",
    "Gengar","Onix","Drowzee","Hypno","Krabby","Kingler","Voltorb",
    "Electrode","Exeggcute","Exeggutor","Cubone","Marowak","Hitmonlee",
    "Hitmonchan","Lickitung","Koffing","Weezing","Rhyhorn","Rhydon","Chansey",
    "Tangela","Kangaskhan","Horsea","Seadra","Goldeen","Seaking","Staryu",
    "Starmie","Mr. Mime","Scyther","Jynx","Electabuzz","Magmar","Pinsir",
    "Tauros","Magikarp","Gyarados","Lapras","Ditto","Eevee","Vaporeon",
    "Jolteon","Flareon","Porygon","Omanyte","Omastar","Kabuto","Kabutops",
    "Aerodactyl","Snorlax","Articuno","Zapdos","Moltres","Dratini",
    "Dragonair","Dragonite","Mewtwo","Mew","Chikorita","Bayleef","Meganium",
    "Cyndaquil","Quilava","Typhlosion","Totodile","Croconaw","Feraligatr",
    "Sentret","Furret","Hoothoot","Noctowl","Ledyba","Ledian","Spinarak",
    "Ariados","Crobat","Chinchou","Lanturn","Pichu","Cleffa","Igglybuff",
    "Togepi","Togetic","Natu","Xatu","Mareep","Flaaffy","Ampharos",
    "Bellossom","Marill","Azumarill","Sudowoodo","Politoed","Hoppip",
    "Skiploom","Jumpluff","Aipom","Sunkern","Sunflora","Yanma","Wooper",
    "Quagsire","Espeon","Umbreon","Murkrow","Slowking","Misdreavus","Unown",
    "Wobbuffet","Girafarig","Pineco","Forretress","Dunsparce","Gligar",
    "Steelix","Snubbull","Granbull","Qwilfish","Scizor","Shuckle","Heracross",
    "Sneasel","Teddiursa","Ursaring","Slugma","Magcargo","Swinub","Piloswine",
    "Corsola","Remoraid","Octillery","Delibird","Mantine","Skarmory",
    "Houndour","Houndoom","Kingdra","Phanpy","Donphan","Porygon2","Stantler",
    "Smeargle","Tyrogue","Hitmontop","Smoochum","Elekid","Magby","Miltank",
    "Blissey","Raikou","Entei","Suicune","Larvitar","Pupitar","Tyranitar",
    "Lugia","Ho-Oh","Celebi",
    # Gen 3 / Hoenn (FRLG+ additions, indices 252-386)
    "Treecko","Grovyle","Sceptile","Torchic","Combusken","Blaziken",
    "Mudkip","Marshtomp","Swampert","Poochyena","Mightyena","Zigzagoon",
    "Linoone","Wurmple","Silcoon","Beautifly","Cascoon","Dustox",
    "Lotad","Lombre","Ludicolo","Seedot","Nuzleaf","Shiftry",
    "Nincada","Ninjask","Shedinja","Taillow","Swellow","Shroomish",
    "Breloom","Spinda","Wingull","Pelipper","Surskit","Masquerain",
    "Wailmer","Wailord","Skitty","Delcatty","Kecleon","Baltoy","Claydol",
    "Nosepass","Torkoal","Sableye","Barboach","Whiscash","Luvdisc",
    "Corphish","Crawdaunt","Feebas","Milotic","Carvanha","Sharpedo",
    "Trapinch","Vibrava","Flygon","Makuhita","Hariyama","Electrike",
    "Manectric","Numel","Camerupt","Spheal","Sealeo","Walrein",
    "Cacnea","Cacturne","Snorunt","Glalie","Lunatone","Solrock",
    "Azurill","Spoink","Grumpig","Plusle","Minun","Mawile","Meditite",
    "Medicham","Swablu","Altaria","Wynaut","Duskull","Dusclops","Roselia",
    "Slakoth","Vigoroth","Slaking","Gulpin","Swalot","Tropius","Whismur",
    "Loudred","Exploud","Clamperl","Huntail","Gorebyss","Absol","Shuppet",
    "Banette","Seviper","Zangoose","Relicanth","Aron","Lairon","Aggron",
    "Castform","Volbeat","Illumise","Lileep","Cradily","Anorith","Armaldo",
    "Ralts","Kirlia","Gardevoir","Bagon","Shelgon","Salamence","Beldum",
    "Metang","Metagross","Regirock","Regice","Registeel","Kyogre","Groudon",
    "Rayquaza","Latias","Latios","Jirachi","Deoxys","Chimecho",
]

# Gen 3 stores a console-internal species index. Indices 1-251 match the
# National Dex; 252-276 are unused; 277-411 are the Hoenn species in *internal*
# order (NOT National Dex order). The _DEX list above appends those Hoenn names
# in that same internal order (just shifted by 25, so internal 277 -> Treecko at
# _DEX position 252), so the NAME for an internal index >=277 is _DEX[idx-26].
# The National Dex number (needed for sprites) requires this explicit table
# (Game Freak's gSpeciesToNationalDexNum), keyed by internal index 277..411.
_HOENN_NAT = [
    252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266,
    267, 268, 269, 270, 271, 272, 273, 274, 275, 290, 291, 292, 276, 277, 285,
    286, 327, 278, 279, 283, 284, 320, 321, 300, 301, 352, 343, 344, 299, 324,
    302, 339, 340, 370, 341, 342, 349, 350, 318, 319, 328, 329, 330, 296, 297,
    309, 310, 322, 323, 363, 364, 365, 331, 332, 361, 362, 337, 338, 298, 325,
    326, 311, 312, 303, 307, 308, 333, 334, 360, 355, 356, 315, 287, 288, 289,
    316, 317, 357, 293, 294, 295, 366, 367, 368, 359, 353, 354, 336, 335, 369,
    304, 305, 306, 351, 313, 314, 345, 346, 347, 348, 280, 281, 282, 371, 372,
    373, 374, 375, 376, 377, 378, 379, 382, 383, 384, 380, 381, 385, 386, 358,
]
assert len(_HOENN_NAT) == 411 - 277 + 1


def species_name(idx):
    if 1 <= idx <= 251:
        return _DEX[idx - 1]
    if 277 <= idx <= 411:            # Hoenn block, internal order
        return _DEX[idx - 26]
    return f"Unknown ({idx})"

def species_dex(idx):
    """National Dex number for sprite lookup, from the Gen 3 internal index."""
    if 1 <= idx <= 251:
        return idx
    if 277 <= idx <= 411:
        return _HOENN_NAT[idx - 277]
    return None


# mapGroup.mapNum -> location on the Kanto map.
# x / y are PERCENT positions on the map image (0-100), so they are
# resolution-independent and easy to re-calibrate.
# Interiors are mapped to their parent town. This table is seeded with the
# spots a Kanto Nuzlocke passes through; unknown maps are logged by the parser
# so they can be added as players explore.
# Coordinates (x%, y%) of each named area on the in-game FRLG Town Map image.
AREA_COORDS = {
    # towns / cities  -- calibrated to the in-game FRLG Town Map (383×287)
    "Pallet Town":    (22, 87), "Viridian City":  (22, 72), "Pewter City":    (22, 33),
    "Cerulean City":  (58, 28), "Lavender Town":  (72, 46), "Vermilion City": (62, 63),
    "Celadon City":   (48, 46), "Fuchsia City":   (43, 76), "Cinnabar Island":(17, 90),
    "Indigo Plateau": (13, 28), "Saffron City":   (62, 46),
    # dungeons / landmarks
    "Viridian Forest": (22, 62), "Mt. Moon":      (33, 30), "S.S. Anne":      (62, 63),
    "Underground Path":(57, 46), "Diglett's Cave": (38, 43), "Victory Road":  (13, 35),
    "Rocket Hideout":  (48, 46), "Silph Co.":     (62, 46), "Pokemon Mansion":(17, 90),
    "Safari Zone":     (38, 72), "Cerulean Cave":  (58, 22), "Rock Tunnel":   (68, 37),
    "Seafoam Islands": (43, 82), "Pokemon Tower":  (72, 46), "Power Plant":   (72, 37),
    # Sevii Islands
    "One Island": (88, 88), "Two Island": (90, 84), "Three Island": (92, 79),
    "Four Island": (88, 71), "Five Island": (90, 65), "Six Island": (92, 59),
    "Seven Island": (88, 54),
}

# Coordinates for the numbered Kanto routes.
ROUTE_COORDS = {
    1: (22, 81),  2: (22, 52),  3: (33, 30),  4: (48, 30),  5: (57, 38),  6: (62, 54),
    7: (57, 46),  8: (72, 46),  9: (68, 33), 10: (72, 37), 11: (62, 63), 12: (72, 56),
    13:(68, 66), 14: (62, 72), 15: (57, 75), 16: (38, 50), 17: (38, 64), 18: (43, 80),
    19:(43, 87), 20: (43, 82), 21: (31, 87), 22: (13, 72), 23: (13, 44), 24: (58, 21),
    25: (65, 18),
}

# Substring rules checked (in order) against the in-game map name.
# Landmarks/dungeons are checked before town tokens so e.g. "ViridianForest"
# resolves to the forest, not Viridian City. Town tokens use the full
# "<Name>City/Town/Island" form so they never collide with a cave/forest.
_LANDMARKS = [
    ("ViridianForest", "Viridian Forest"), ("MtMoon", "Mt. Moon"),
    ("SSAnne", "S.S. Anne"), ("UndergroundPath", "Underground Path"),
    ("DiglettsCave", "Diglett's Cave"), ("VictoryRoad", "Victory Road"),
    ("RocketHideout", "Rocket Hideout"), ("SilphCo", "Silph Co."),
    ("PokemonMansion", "Pokemon Mansion"), ("SafariZone", "Safari Zone"),
    ("CeruleanCave", "Cerulean Cave"), ("PokemonLeague", "Indigo Plateau"),
    ("RockTunnel", "Rock Tunnel"), ("SeafoamIslands", "Seafoam Islands"),
    ("PokemonTower", "Pokemon Tower"), ("PowerPlant", "Power Plant"),
    # Sevii landmarks
    ("MtEmber", "One Island"), ("BerryForest", "Three Island"),
    ("TrainerTower", "Seven Island"), ("TanobyRuins", "Seven Island"),
    ("SevaultCanyon", "Seven Island"),
]
_TOWNS = [
    ("PalletTown", "Pallet Town"), ("ViridianCity", "Viridian City"),
    ("PewterCity", "Pewter City"), ("CeruleanCity", "Cerulean City"),
    ("LavenderTown", "Lavender Town"), ("VermilionCity", "Vermilion City"),
    ("CeladonCity", "Celadon City"), ("FuchsiaCity", "Fuchsia City"),
    ("CinnabarIsland", "Cinnabar Island"), ("IndigoPlateau", "Indigo Plateau"),
    ("SaffronCity", "Saffron City"),
]
_ISLANDS = [
    ("OneIsland", "One Island"), ("TwoIsland", "Two Island"),
    ("ThreeIsland", "Three Island"), ("FourIsland", "Four Island"),
    ("FiveIsland", "Five Island"), ("SixIsland", "Six Island"),
    ("SevenIsland", "Seven Island"),
]


def _prettify(name):
    base = name.split("_")[0]
    return re.sub(r"(?<=[a-z])(?=[A-Z0-9])", " ", base)


def _resolve_area(name):
    for kw, area in _LANDMARKS:
        if kw in name:
            return area, AREA_COORDS[area]
    for kw, area in _TOWNS:
        if kw in name:
            return area, AREA_COORDS[area]
    m = re.search(r"Route(\d+)", name)
    if m and int(m.group(1)) in ROUTE_COORDS:
        n = int(m.group(1))
        return f"Route {n}", ROUTE_COORDS[n]
    for kw, area in _ISLANDS:
        if kw in name:
            return area, AREA_COORDS[area]
    return _prettify(name), None


def lookup_location(group, num, region="kanto"):
    """Resolve a save's mapGroup.mapNum to an area + map coordinates.

    Kanto (FRLG) resolves via the decomp-generated map-name table; other regions
    (e.g. the Johto romhack) use their own raw group.num -> coords tables.
    """
    if region == "johto":
        return johtodata.lookup_location(group, num)

    name = mapdata.MAP_NAMES.get(f"{group}.{num}")
    if not name:
        return {"area": "Unknown", "x": 50.0, "y": 50.0, "known": False}
    area, xy = _resolve_area(name)
    x, y = xy if xy else (50.0, 50.0)
    return {"area": area, "x": float(x), "y": float(y), "known": xy is not None}
