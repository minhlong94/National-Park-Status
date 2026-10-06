#!/usr/bin/env python3
"""Build data/park-bounds.js: a simple outline of each park and the NWS zones that touch it.

The page uses this file to find the NWS alerts for the whole park, not only for one point (R32):
- An alert with a polygon (for example a Flash Flood Warning) applies if the polygon touches the park outline.
- An alert without a polygon (for example a Flood Watch) applies if one of its zones touches the park.

Sources:
- Park outlines: NPS Land Resources Division boundary service (ArcGIS).
- NWS forecast zones and county zones: api.weather.gov.

Park boundaries and NWS zones change very little, so no schedule runs this script.
The workflow .github/workflows/build-bounds.yml runs it when the script changes, or from the Actions tab.
Requires shapely (pip install shapely).
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import datetime as dt
from pathlib import Path

from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely.validation import make_valid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_history as fh  # noqa: E402  (load_parks)

ROOT = fh.ROOT
OUT = ROOT / "data" / "park-bounds.js"
BOUNDS_URL = ("https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/"
              "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2/query")
NWS = "https://api.weather.gov"
UA = {"User-Agent": "National-Park-Status (https://github.com/minhlong94/National-Park-Status)",
      "Accept": "application/geo+json"}
MAX_POINTS = 300          # the most outline points for one park
MIN_SHARE = 0.002         # a zone must cover this part of the park (or 2 km2), so a zone that only touches the edge is left out
# Unit codes in the boundary data that are not the same as the park code in index.html
UNIT_CODES = {"seki": ["SEQU", "SEKI"], "kica": ["KICA", "SEKI"]}


def get(url, tries=4, timeout=60):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"  retry {k + 1}: {e} {url[:120]}", flush=True)
            time.sleep(3 * (k + 1))
    raise RuntimeError("failed: " + url)


def park_shape(p):
    for code in UNIT_CODES.get(p["id"], [p["id"].upper()]):
        q = urllib.parse.urlencode({"where": f"UNIT_CODE='{code}'", "outFields": "UNIT_CODE,UNIT_NAME",
                                    "returnGeometry": "true", "outSR": "4326", "geometryPrecision": "4",
                                    "maxAllowableOffset": "0.001", "f": "geojson"})
        j = get(f"{BOUNDS_URL}?{q}")
        feats = j.get("features") or []
        if feats:
            g = unary_union([make_valid(shape(f["geometry"])) for f in feats if f.get("geometry")])
            g = unary_union([x for x in getattr(g, "geoms", [g]) if x.geom_type in ("Polygon", "MultiPolygon")])
            print(f"{p['id']}: {code} {feats[0]['properties'].get('UNIT_NAME')}", flush=True)
            return g
    print(f"{p['id']}: NO BOUNDARY, uses a 5 km box at the park point", flush=True)
    return Point(p["lon"], p["lat"]).buffer(0.05)


def simplify(g):
    tol = 0.002
    while True:
        s = g.simplify(tol, preserve_topology=True)
        polys = list(s.geoms) if s.geom_type == "MultiPolygon" else [s]
        # Leave out very small parts (islands, small tracts), but keep at least the largest part.
        polys.sort(key=lambda x: -x.area)
        keep = [x for x in polys if x.area >= polys[0].area * 0.01] or polys[:1]
        n = sum(len(x.exterior.coords) for x in keep)
        if n <= MAX_POINTS or tol > 0.2:
            return [[[round(x, 3), round(y, 3)] for x, y in poly.exterior.coords] for poly in keep]
        tol *= 1.6


def zones_for(area, kind):
    """All NWS zones of one type in one state or territory, with their shapes."""
    j = get(f"{NWS}/zones?type={kind}&area={area}&include_geometry=true", timeout=120)
    out = []
    for f in j.get("features") or []:
        if f.get("geometry"):
            try:
                out.append((f["properties"]["id"], make_valid(shape(f["geometry"]))))
            except Exception:  # noqa: BLE001
                pass
    return out


def main():
    parks = fh.load_parks()
    shapes = {p["id"]: park_shape(p) for p in parks}
    # The states and territories of each park, from the "st" value in index.html (for example "WY / MT / ID").
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    st = {}
    for m in re.finditer(r'code:"(\w+)",(?: id:"(\w+)",)? name:"[^"]+", st:"([^"]+)"', html):
        st[m.group(2) or m.group(1)] = [{"USVI": "VI"}.get(x.strip(), x.strip()) for x in m.group(3).split("/")]
    areas = sorted({a for p in parks for a in st.get(p["id"], [])})
    print("areas:", areas, flush=True)
    zones = {}
    for a in areas:
        for kind in ("forecast", "county"):
            try:
                zones.setdefault(a, []).extend(zones_for(a, kind))
            except RuntimeError as e:
                print("  zones failed:", a, kind, e, flush=True)
        print(f"zones {a}: {len(zones.get(a, []))}", flush=True)
    out = {}
    for p in parks:
        g = shapes[p["id"]]
        b = g.bounds
        hit = []
        for a, zs in zones.items():
            for zid, zg in zs:
                if not zg.intersects(g):
                    continue
                share = zg.intersection(g).area
                if share >= min(g.area * MIN_SHARE, 0.0002) or zg.contains(g.representative_point()):
                    hit.append(zid)
        hit = sorted(set(hit))
        out[p["id"]] = {"b": [round(b[0], 3), round(b[1], 3), round(b[2], 3), round(b[3], 3)],
                        "p": simplify(g), "z": hit}
        print(f"  {p['id']}: {sum(len(r) for r in out[p['id']]['p'])} points, {len(hit)} zones", flush=True)
    data = {"source": "NPS Land Resources Division park boundaries; NWS forecast and county zones (api.weather.gov)",
            "built": dt.date.today().isoformat(), "parks": out}
    OUT.write_text("// Generated by scripts/build_bounds.py. Do not edit by hand.\n"
                   "// b = box [west, south, east, north]. p = simple outline rings [lon, lat]. z = NWS zones that touch the park.\n"
                   "window.PARK_BOUNDS = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
