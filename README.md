# Kanto Nuzlocke Tracker

A small website that reads Pokémon FireRed/LeafGreen `.sav` files and shows each
player's progress on the in-game Kanto Town Map. Click a player's face to see
their name, badges, current party, PC boxes, and play time.

## How it works

```
.sav files  ──►  parse_saves.py  ──►  site/data.json  ──►  static website
```

1. **`parse_saves.py`** reads every `.sav` in `saves/`, decodes the Gen 3 save
   format (trainer info, party, PC boxes, badges, location) and writes
   `site/data.json`.
2. **`site/`** is a plain HTML/CSS/JS site that loads `data.json`, places a
   marker on the Town Map for each player, and shows a detail panel on click.

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
# Drop .sav files into saves/, then:
python parse_saves.py
python -m http.server 8000 --directory site
```

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
