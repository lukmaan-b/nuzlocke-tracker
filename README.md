# Nuzlocke Tracker

A small website that reads Pokémon Gen 3 `.sav`/`.srm` files and shows each
player's progress on the in-game region map. Click a player's face to see their
name, badges, current party, PC boxes, and play time. Multiple games/regions are
supported and switched between with pills (e.g. a Johto romhack on the front
page, the original Kanto FireRed run as a second tab).

## How it works

```
saves/<game>/*.srm  ──►  parse_saves.py  ──►  docs/data.json  ──►  static website
                              ▲
                          games.json (per-game: region, map, badges, save format)
```

1. **`games.json`** lists each game: its save folder, save `format`
   (`frlg` or `emerald`), `region`, map image, and badge names.
2. **`parse_saves.py`** reads every save in each game's folder, decodes the Gen 3
   save format (trainer info, party, PC boxes, badges, location) and writes
   `docs/data.json` grouped by game.
3. **`docs/`** is a plain HTML/CSS/JS site that loads `data.json`, renders a pill
   per game, places a marker on that game's map for each player, and shows a
   detail panel on click.

## Usage

### With Dropbox (recommended)

1. Create `C:\Users\lukma\poke-nuzlocke\.env` (copy from `.env.example`):
   ```
   DROPBOX_TOKEN=sl.u.XXXX...
   DROPBOX_SAVE_FOLDER=/nuzlocke
   ```
2. Everyone uploads their `.sav` to the shared Dropbox folder (file must be named
   after their player ID, e.g. `lukmaan.sav`).
3. Run once to test:
   ```powershell
   python poll_dropbox.py
   ```
4. Schedule daily auto-sync:
   ```powershell
   .\setup_scheduler.ps1
   ```
5. Serve the site:
   ```powershell
   python -m http.server 8000 --directory site
   ```

### Manual (no Dropbox)

```powershell
# Drop each save into its game's folder, e.g.
#   saves/johto/<player>.srm   (Emerald-based HG/SS romhack)
#   saves/firered/<player>.sav (FireRed/LeafGreen)
# then:
python parse_saves.py
python -m http.server 8000 --directory docs
```

### Adding a new game

Add an entry to `games.json` (id, name, `savesDir`, `format`, `region`,
`mapImage`, `badges`) and drop a region map into `docs/assets/`. For a region
without a decomp map-name table (like the Johto romhack), locations are mapped by
raw `mapGroup.mapNum` in `johtodata.py` — the parser logs any unmapped
`group.num` so you can add it as players explore.

### Migration (single-game → multi-game)

This used to be a single Kanto/FireRed tracker; it's now multi-game. If you have
an old checkout:

- **Save files moved into per-game folders.** Old: `saves/*.sav`. New:
  `saves/<game>/*.{sav,srm}` (e.g. `saves/firered/wes.sav`,
  `saves/johto/wes.srm`). `games.json` points each game at its folder via
  `savesDir`.
- **`parse_saves.py` args changed.** It now takes `[games.json] [out.json]`
  (was `[saves_dir] [out.json]`) and writes `{ "games": [...] }` instead of a
  top-level `{ "players": [...] }`.
- **`e4_records.json` keys are namespaced** `"<game>/<player>"` (was just
  `"<player>"`), so one person can clear multiple games. Existing keys were
  migrated to the `firered/` prefix.
- **`docs/data.json` is regenerated** — just re-run `python parse_saves.py`.
- The frontend reads the new grouped shape but still falls back to an old
  top-level `players` array if it sees one.

## Player avatars

The marker (and detail-panel header) shows, in priority order:

1. the sprite of the **lead (first) party Pokémon**,
2. a player photo at `site/faces/<id>.png` (if present),
3. a colored circle with the trainer's initial (used when the party is empty).

To add real photos, drop an image named after the save file into `site/faces/`,
e.g. `saves/lukmaan.sav` → `site/faces/lukmaan.png`.

## Map locations

Locations are fully resolved, not guessed. `mapdata.py` is auto-generated from
the pokefirered decomp and maps every `mapGroup.mapNum` (425 maps) to its in-game
map name. `gen3data.py` then resolves that name to an area + Town-Map coordinates,
handling towns, all interiors (gyms, Centers, houses), every route, dungeons
(Mt. Moon, Rock Tunnel, Victory Road, Silph Co., Safari Zone, …) and the Sevii
Islands. Verified against real saves (Pallet Town, Route 2). Anything still
unrecognised prints a `[!] unmapped location` line and renders at map center.

## Known limitations / TODO

- **Party decoding is validated** against a real mid-game save (Rattata/Squirtle/
  Pidgey read correctly with levels + HP). Box decoding uses the same checksummed
  routine but hasn't been seen against a full PC yet; boxed Pokémon don't show a
  level (Gen 3 stores experience, not level, for boxed mons — would need the
  per-species growth tables to derive it).
- Held-item and move names aren't resolved yet (species, nickname, level, HP,
  shiny, and egg status are).
- Pokémon sprites load from the PokeAPI sprite CDN by National Dex number.
- **Johto romhack: Kanto post-game is not tracked.** The romhack is HG/SS-based
  and continues into Kanto after the 8 Johto badges (badges 9–16, Indigo
  Plateau, Mt. Silver). Only Johto is supported so far: the map asset
  (`docs/assets/johto-map.png`, ripped from the in-game Town Map) covers Johto
  only, and the game's `badges` list in `games.json` is the 8 Johto badges, so
  Kanto badges/locations won't show. Adding it later means a Kanto map + Kanto
  `mapGroup.mapNum` coordinates in `johtodata.py` and 16-badge handling.
- **Johto town coordinates are approximate.** The in-game map markers are
  unlabeled, so `johtodata.AREA_COORDS` was matched to Johto geography by hand —
  only Violet City is confirmed. Correct the rest as players visit each town.

## Files

| File | Purpose |
|------|---------|
| `parse_saves.py` | Save-folder → `site/data.json` |
| `gen3data.py` | Species names + map location resolver |
| `mapdata.py` | Auto-generated `group.num` → map name (from pokefirered) |
| `saves/` | Drop `.sav` files here |
| `site/index.html`, `style.css`, `app.js` | The website |
| `site/assets/townmap.png` | Kanto Town Map background |
| `site/faces/` | Optional player photos (`<id>.png`) |
| `site/data.json` | Generated data (do not edit by hand) |
