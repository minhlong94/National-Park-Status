#!/usr/bin/env python3
"""Keep data/foliage-grid.js: the usual fall color timing on a grid across the US, for the regional map.

Source: NASA MODIS land surface phenology (MCD12Q2), ORNL DAAC MODIS web service.
For each grid point in data/foliage-grid-cells.json and each of the last 5 years with data:
the median day of the year (Jan 1 = 0) in a 21 km x 21 km box when greenness starts to drop (sen),
the middle of the drop (mid) and leaves off (dor). The file keeps the average over the years.

The data changes once a year. The script:
1. Continues an unfinished grid (about 1,300 requests in all). It stops before its time limit,
   saves what it has, and the next run continues.
2. Checks for a new NASA year only when the grid is complete. It first checks one point in the
   Great Smoky Mountains. If that point has no data for the new year, the script stops.
   If it has data, the script starts a new grid for the new 5 years.

Run: python3 scripts/fetch_foliage_grid.py
"""
import datetime as dt
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_history as fh   # noqa: E402  (get_json with timeouts)
import fetch_foliage as ff   # noqa: E402  (MODIS helpers)

fh.SCRIPT_DEADLINE = 45 * 60      # stop and save before the workflow step limit; the next run continues
ROOT = fh.ROOT
CELLS = ROOT / "data" / "foliage-grid-cells.json"
OUT = ROOT / "data" / "foliage-grid.js"
YEARS = 5                         # the number of recent years to average
KM = 10                           # 10 km above, below, left and right: a 21 km x 21 km box
MIN_YEARS = 3                     # a point needs a growing cycle in at least this many years
MIN_SHARE = 0.10                  # a year counts if at least 10% of the pixels have a cycle
PROBE = (35.5, -84.0)             # a forest point in the Great Smoky Mountains
SAVE_EVERY = 20
DATE_BANDS = ("sen", "mid", "dor")   # the greenness-change band (amp) is not needed for the map


def date_bands():
    return {k: v for k, v in ff.band_names().items() if k in DATE_BANDS}


def key(c):
    return f"{c['lat']},{c['lon']}"


def cell_values(lat, lon, bands, years, min_years=MIN_YEARS):
    """Returns [sen, mid, dor] (days of the year, averaged over the years) or 0 if there is no clear cycle."""
    per_year = {y: {} for y in years}
    for k, band in bands.items():
        data = ff.modis_get(f"{ff.PRODUCT}/subset", latitude=lat, longitude=lon, band=band,
                            startDate=f"A{years[0]}001", endDate=f"A{years[-1]}365",
                            kmAboveBelow=KM, kmLeftRight=KM)
        for s in data.get("subset", []):
            y = int(s["calendar_date"][:4])
            if y not in per_year:
                continue
            jan1 = (dt.date(y, 1, 1) - dt.date(1970, 1, 1)).days
            vals = s.get("data", [])
            good = [v - jan1 for v in vals if v is not None and jan1 <= v <= jan1 + 430]
            per_year[y][k] = statistics.median(good) if vals and len(good) >= MIN_SHARE * len(vals) else None
    rows = [[per_year[y].get(k) for k in ("sen", "mid", "dor")] for y in years]
    rows = [r for r in rows if None not in r]
    if len(rows) < min_years:
        return 0
    return [round(sum(r[i] for r in rows) / len(rows)) for i in range(3)]


def read_store():
    s = ff.read_js(OUT, "FOLIAGE_GRID")
    return s if s and s.get("format") == 1 else None


def save(store, cells):
    store["done"] = sum(1 for c in cells if key(c) in store["cells"])
    store["total"] = len(cells)
    store["updated"] = dt.date.today().isoformat()
    ff.write_js(OUT, "FOLIAGE_GRID", store,
                "cells: 'lat,lon' -> [sen, mid, dor] (day of the year, Jan 1 = 0), or 0 when there is no clear fall color.")


def main():
    grid = json.loads(CELLS.read_text(encoding="utf-8"))
    cells = grid["cells"]
    store = read_store()
    bands = None

    complete = store is not None and all(key(c) in store["cells"] for c in cells)
    if complete:
        # Step 1: check for a new NASA year at the probe point only.
        avail = ff.available_years({"lat": PROBE[0], "lon": PROBE[1]})
        newest = max(avail) if avail else None
        if not newest or newest <= max(store["years"]):
            print(f"The grid is complete for {store['years']}. No new year. Nothing to do.")
            return
        bands = date_bands()
        years = list(range(newest - YEARS + 1, newest + 1))
        probe = cell_values(PROBE[0], PROBE[1], bands, [newest], min_years=1)
        if not probe:
            print(f"The probe point has no data for {newest}. The script stops here.")
            return
        print(f"New year {newest}. Starting a new grid for {years}.", flush=True)
        store = {"format": 1, "years": years, "cells": {}}
    elif store is None:
        avail = ff.available_years({"lat": PROBE[0], "lon": PROBE[1]})
        newest = max(avail)
        store = {"format": 1, "years": list(range(newest - YEARS + 1, newest + 1)), "cells": {}}
        print(f"Starting a new grid for {store['years']}.", flush=True)
    else:
        print(f"Continuing the grid for {store['years']}: {len(store['cells'])} of {len(cells)} points done.", flush=True)

    bands = bands or date_bands()
    store["about"] = "NASA MODIS land surface phenology (MCD12Q2), ORNL DAAC MODIS web service. Median of a 21 km box, average of the years."
    todo = [c for c in cells if key(c) not in store["cells"]]
    since_save = 0
    try:
        for i, c in enumerate(todo):
            fh.time_left()  # raises DeadlineExceeded near the time limit
            print(f"point {len(store['cells']) + 1} of {len(cells)}: {c['lat']}, {c['lon']} ({c['st']})", flush=True)
            store["cells"][key(c)] = cell_values(c["lat"], c["lon"], bands, store["years"])
            since_save += 1
            if since_save >= SAVE_EVERY:
                save(store, cells)
                since_save = 0
            time.sleep(0.3)
    except fh.DeadlineExceeded:
        print("Time limit reached. The next run continues from here.", flush=True)
    finally:
        save(store, cells)
    left = len(cells) - len(store["cells"])
    print(f"{len(store['cells'])} of {len(cells)} points done. {left} left.")


if __name__ == "__main__":
    main()
