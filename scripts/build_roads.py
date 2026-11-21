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
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
UA = {"User-Agent": "National-Park-Status (https://github.com/minhlong94/National-Park-Status)"}
MAIN = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified"}
MINOR = {"residential", "service", "track"}   # only with a name, and only when long enough
SIMPLIFY = 0.0006                             # degrees (about 60 m)
MAX_ROADS = 60                                # the longest roads of a park


def load_bounds():
    m = re.search(r"window\.PARK_BOUNDS = (\{.*\});", BOUNDS.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1))["parks"]


def overpass(query):
    last = None
    for k in range(6):
        url = OVERPASS[k % len(OVERPASS)]
        try:
            req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": query}).encode(), headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  retry {k + 1}: {e}", flush=True)
            time.sleep(10 * (k + 1))
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
    area = shape.buffer(0.01)  # about 1 km of margin: roads on the boundary stay
    q = (f'[out:json][timeout:170];way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|'
         f'residential|service|track)$"]({s - 0.01},{w - 0.01},{n + 0.01},{e + 0.01});out geom;')
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


def main():
    bounds = load_bounds()
    only = set(sys.argv[1:])
    out = {}
    for pid, rec in sorted(bounds.items()):
        if only and pid not in only:
            continue
        try:
            roads = park_roads(pid, rec)
        except RuntimeError as e:
            sys.exit(f"{pid}: {e}")
        out[pid] = roads
        print(f"  {pid}: {len(roads)} roads, {sum(len(c) for r in roads for c in r['l'])} points:"
              f" {[r['n'] for r in roads[:8]]}", flush=True)
        time.sleep(2)
    data = {"source": "OpenStreetMap contributors (ODbL), Overpass API", "built": dt.date.today().isoformat(), "parks": out}
    OUT.write_text("// Generated by scripts/build_roads.py. Do not edit by hand. Road lines © OpenStreetMap contributors (ODbL).\n"
                   "// n = road name, m = 1 for a main road, l = lines [[lon, lat], ...].\n"
                   "window.PARK_ROADS = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
