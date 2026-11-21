#!/usr/bin/env python3
"""Build data/park-roads.js: the main roads inside each park, for the road closure overview map (R67).

The page draws a small map of each park: the park outline (data/park-bounds.js) and these roads.
It marks the roads that are closed now, from the closure data that the page already has
(NPS alerts, live road status, park road condition tables, seasonal road dates).

Source: OpenStreetMap (© OpenStreetMap contributors, ODbL), through the Overpass API.
For each park the script:
1. gets the roads for cars in the box of the park (and named tracks),
2. keeps the parts inside the park outline (with a small margin),
3. joins the parts that have the same name, and simplifies the lines.

Roads change very little, so no schedule runs this script. The workflow
.github/workflows/build-roads.yml runs it when the script changes, or from the Actions tab.
Requires shapely (pip install shapely).
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import linemerge, unary_union

ROOT = Path(__file__).resolve().parent.parent
BOUNDS = ROOT / "data" / "park-bounds.js"
OUT = ROOT / "data" / "park-roads.js"
OVERPASS = "https://overpass-api.de/api/interpreter"
PAUSE = 12                                    # seconds between parks: the server sends 502 errors to fast clients
DEADLINE = 40 * 60                            # seconds: then the script saves the parks it has, and the next run continues
UA = {"User-Agent": "National-Park-Status (https://github.com/minhlong94/National-Park-Status)"}
MAIN = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified"}
MINOR = {"service", "track"}                 # only with a name, and only when long enough (no town streets)
SIMPLIFY = 0.0006                             # degrees (about 60 m)
MAX_ROADS = 40                                # the longest roads of a park
MARGIN = 0.002                                # degrees (about 200 m) outside the park outline
START = time.monotonic()


def load_bounds():
    m = re.search(r"window\.PARK_BOUNDS = (\{.*\});", BOUNDS.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1))["parks"]


def overpass(query):
    last = None
    for k in range(5):
        try:
            req = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": query}).encode(), headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  retry {k + 1}: {e}", flush=True)
            time.sleep(20 * (k + 1))
    raise RuntimeError(f"Overpass failed: {last}")


def km(line, lat):
    """Approximate length in km of a line in degrees."""
    import math
    return line.length * 111 * max(0.3, math.cos(math.radians(lat)) ** 0.5)


def _lines(g):
    """The simple lines in a geometry (a clip can give lines, multi lines, points or a collection)."""
    if isinstance(g, LineString):
        return [g] if not g.is_empty and g.length > 0 else []
    return [x for sub in getattr(g, "geoms", []) for x in _lines(sub)]


def park_roads(pid, rec):
    w, s, e, n = rec["b"]
    shape = unary_union([Polygon(r).buffer(0) for r in rec["p"] if len(r) >= 4])
    area = shape.buffer(MARGIN)  # a small margin: roads on the boundary stay
    q = (f'[out:json][timeout:100];way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|'
         f'service|track)$"]({s - MARGIN},{w - MARGIN},{n + MARGIN},{e + MARGIN});out geom;')
    j = overpass(q)
    by_name = {}
    for el in j.get("elements", []):
        tags = el.get("tags", {})
        hw, name = tags.get("highway"), (tags.get("name") or tags.get("ref") or "").strip()
        if hw in MINOR and not tags.get("name"):
            continue
        if hw == "service" and tags.get("service"):
            continue  # parking aisles, driveways
        pts = [(g["lon"], g["lat"]) for g in el.get("geometry", [])]
        if len(pts) < 2:
            continue
        part = LineString(pts).intersection(area)
        if part.is_empty:
            continue
        key = (name, "main" if hw in MAIN else "minor")
        by_name.setdefault(key, []).append(part)
    roads = []
    lat = (s + n) / 2
    for (name, cls), parts in by_name.items():
        lines = [x for x in (flat for part in parts for flat in _lines(part))]
        if len(lines) > 1:
            lines = list(_lines(linemerge(MultiLineString(lines))))
        total = sum(km(l, lat) for l in lines)
        if cls == "minor" and total < 1.5:
            continue
        if not name and total < 3:
            continue
        simple = [l.simplify(SIMPLIFY) for l in lines]
        coords = [[[round(x, 4), round(y, 4)] for x, y in l.coords] for l in simple if len(l.coords) >= 2]
        if coords:
            roads.append({"n": name, "m": 1 if cls == "main" else 0, "l": coords, "_km": total})
    roads.sort(key=lambda r: (-r["m"], -r["_km"]))
    roads = roads[:MAX_ROADS]
    for r in roads:
        r.pop("_km")
    return roads


def save(out):
    data = {"source": "OpenStreetMap contributors (ODbL), Overpass API", "built": dt.date.today().isoformat(),
            "parks": dict(sorted(out.items()))}
    OUT.write_text("// Generated by scripts/build_roads.py. Do not edit by hand. Road lines © OpenStreetMap contributors (ODbL).\n"
                   "// n = road name, m = 1 for a main road, l = lines [[lon, lat], ...].\n"
                   "window.PARK_ROADS = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")


def main():
    """Build the parks that are not in the file yet (all parks with --all, or the parks named on the command line).
    The script saves after each park. At DEADLINE it stops; the next run continues with the parks that are left."""
    bounds = load_bounds()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = {}
    if OUT.exists() and "--all" not in sys.argv:
        m = re.search(r"window\.PARK_ROADS = (\{.*\});", OUT.read_text(encoding="utf-8"), re.S)
        out = json.loads(m.group(1))["parks"] if m else {}
    todo = [pid for pid in sorted(bounds) if (pid in args) or (not args and pid not in out)]
    print(f"{len(out)} parks in the file, {len(todo)} to build.", flush=True)
    for k, pid in enumerate(todo):
        if time.monotonic() - START > DEADLINE:
            print(f"Time limit: {len(todo) - k} parks are left. Run the workflow again to continue.", flush=True)
            break
        try:
            roads = park_roads(pid, bounds[pid])
        except RuntimeError as e:
            print(f"  {pid}: {e}. The next run tries again.", flush=True)
            continue
        out[pid] = roads
        save(out)
        print(f"  {pid}: {len(roads)} roads, {sum(len(c) for r in roads for c in r['l'])} points:"
              f" {[r['n'] for r in roads[:8]]}", flush=True)
        time.sleep(PAUSE)
    save(out)
    print("wrote", OUT, OUT.stat().st_size, "bytes,", len(out), "parks")


if __name__ == "__main__":
    main()
