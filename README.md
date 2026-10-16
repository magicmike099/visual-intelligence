# Paris Manif Map

A phone app that shows protest and disruption zones in Paris for Saturday 17 October 2026, flags walking routes that cross them, and works offline once installed.

- `docs/` is the installable app. GitHub Pages serves it (Settings → Pages → Branch `main`, folder `/docs`).
- **My places**: import the places you saved in Google Maps (Google Takeout `Saved Places.json`, KML, CSV with coordinates, or pasted links). The app shows which ones are in or near a zone at any time of day. They are stored only in the browser on your phone.
- `tools/` holds the scripts that build the zone data (`zones.py`), the Google My Maps layer (`kml.py`) and the installable package (`pwa.py`).

The zone data is built from press reports and is unofficial. Check the Préfecture de police and RATP before travelling. Street data is © OpenStreetMap contributors via Overture Maps.
