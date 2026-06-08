"""Static lookup tables for Gen 3 (FireRed/LeafGreen) save parsing."""
import re
import mapdata  # auto-generated "group.num" -> in-game map name

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

def species_name(idx):
    if 1 <= idx <= len(_DEX):
        return _DEX[idx - 1]
    return f"Unknown ({idx})"

def species_dex(idx):
    """National Dex number for sprite lookup.
    FRLG vanilla: internal 1-251 == National Dex.
    FRLG+ adds Hoenn mons at internal 252-386, same as National Dex."""
    if 1 <= idx <= 386:
        return idx
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


def lookup_location(group, num):
    name = mapdata.MAP_NAMES.get(f"{group}.{num}")
    if not name:
        return {"area": "Unknown", "x": 50.0, "y": 50.0, "known": False}
    area, xy = _resolve_area(name)
    x, y = xy if xy else (50.0, 50.0)
    return {"area": area, "x": float(x), "y": float(y), "known": xy is not None}
