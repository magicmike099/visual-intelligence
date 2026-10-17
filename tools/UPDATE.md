# How the hourly zone update works (notes for whoever runs it)

1. Edit `zones.py` (zone list, times, headline), then run in this folder: `python3 zones.py`, `python3 kml.py`, `python3 pwa.py`.
2. Rebuild `paris-manif-map-app.zip` from the contents of `pwa/`.
3. Copy `pwa/*` into the repo clone `docs/` and `zones.json`, `zones.py`, `kml.py`, `index.html`, `pwa.py` into `tools/`, commit and push to `main` (repo `magicmike099/visual-intelligence`).
4. Republish the preview page: copy `index.html`, `zones.json`, `paris.json`, `glyphs.json` into the session scratchpad folder `art/` and publish `art/index.html` to https://claude.ai/artifact/5saF3xgrEvUL8PdSGgGBzH with those three json files in `files`. `index.html` here keeps the unpkg MapLibre tag; `pwa.py` swaps it for the bundled `ml.js`.

The app keeps saved places only in the user's browser (localStorage key `manif.places.v1`), so zone updates never touch them.

## Zone fields that control what is drawn

Each zone in `zones.py` carries an `outcome`:
- `official`: a prefecture order (bans). Drawn between `start` and `end`.
- `observed`: a press report says it happened. Drawn between `start` and `end`; set `seen` to the time of the latest report and `end` to about an hour after it, then push `end` forward when newer reports appear.
- `planned`: announced and not started when `updated` was written. Drawn only while its start is still after `updated`.
- `unconfirmed`: start time passed and no report found. Not drawn; listed under "Not on the map".
- `cancelled`: reported cancelled (add `moved='to <place>'` if it moved, and add the new place as its own `observed` zone). Not drawn.
Zones without `outcome` are treated as `official`. `kml.py` leaves out `unconfirmed` and `cancelled` zones.

## Several days

`zones.py` ends with a `days=[...]` list. Each entry has `day`, `label` (shown on the day chip), `chips` (time chips), `focus` (time the day opens on when it is not today) and, for days after the first, its own `headline`, `traffic`, `src` and `transit` notes (métro, RER and tram works shown on the Today tab). The first day (Saturday) keeps using the top-level `headline` and `traffic`. A zone belongs to the first day unless it has `day='YYYY-MM-DD'`. The app opens on today's day when it is in the list. Stations (`STATIONS`) belong to the first day only. `kml.py` writes the first day in its usual folders and every later day in one folder.
