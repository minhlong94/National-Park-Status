#!/usr/bin/env python3
"""Build data/park-history.js: monthly visits and monthly climate for each park.

Visits:  NPS Visitor Use Statistics (irmaservices.nps.gov), recreation visits per month.
Weather: Open-Meteo historical archive (archive-api.open-meteo.com), daily values
         aggregated per month and averaged over the same years.

The script reads the park list (id, code, lat, lon) from index.html, so the page
stays the single source for the park list. It uses the last 3 complete calendar years.
Standard library only. Run: python3 scripts/fetch_history.py
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS_BACK = 3
# NPS Visitor Use Statistics reports Sequoia and Kings Canyon as separate units.
STATS_CODE = {"seki": "SEQU", "kica": "KICA"}


def get_json(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "National-Park-Status data script"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # network or rate-limit errors: wait, then try again
            print(f"  attempt {i + 1} failed: {e}", file=sys.stderr)
            if i == tries - 1:
                raise
            time.sleep(5 * 2 ** i)


def load_parks():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parks = []
    for m in re.finditer(r'\{r:(\d+), code:"(\w+)",(?: id:"(\w+)",)? name:"([^"]+)".*?lat:(-?[\d.]+), lon:(-?[\d.]+)', html):
        r, code, pid, name, lat, lon = m.groups()
        parks.append({"id": pid or code, "code": code, "name": name, "lat": float(lat), "lon": float(lon)})
    if len(parks) != 63:
        sys.exit(f"Expected 63 parks in index.html, found {len(parks)}")
    return parks


def find_key(rec, *patterns):
    for k in rec:
        if any(re.fullmatch(p, k, re.I) for p in patterns):
            return k
    return None


def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for v in payload.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return []


def fetch_visits(parks, years):
    codes = sorted({STATS_CODE.get(p["id"], p["id"].upper()) for p in parks})
    out = {}
    for i in range(0, len(codes), 20):
        batch = codes[i:i + 20]
        q = urllib.parse.urlencode({"unitCodes": ",".join(batch), "startMonth": 1, "startYear": years[0],
                                    "endMonth": 12, "endYear": years[-1]})
        url = "https://irmaservices.nps.gov/v3/rest/stats/visitation?" + q
        print("GET", url)
        recs = records(get_json(url))
        if not recs:
            sys.exit("Visitor statistics: empty response")
        if i == 0:
            print("  sample record:", json.dumps(recs[0])[:400])
        k_unit = find_key(recs[0], r"unit_?code")
        k_year = find_key(recs[0], r"year")
        k_month = find_key(recs[0], r"month")
        k_vis = find_key(recs[0], r"recreation_?visit(or)?s?")
        if not all([k_unit, k_year, k_month, k_vis]):
            sys.exit(f"Visitor statistics: unknown fields {list(recs[0])}")
        for rec in recs:
            y, mth = int(rec[k_year]), int(rec[k_month])
            if y in years and 1 <= mth <= 12:
                v = rec[k_vis]
                out.setdefault(rec[k_unit].upper(), {}).setdefault(str(y), [None] * 12)[mth - 1] = None if v is None else int(v)
        time.sleep(1)
    result = {}
    for p in parks:
        code = STATS_CODE.get(p["id"], p["id"].upper())
        if code not in out:
            print(f"  WARNING: no visits for {p['name']} ({code})", file=sys.stderr)
        result[p["id"]] = {str(y): out.get(code, {}).get(str(y), [None] * 12) for y in years}
    return result


def fetch_weather(p, years):
    q = urllib.parse.urlencode({
        "latitude": p["lat"], "longitude": p["lon"],
        "start_date": f"{years[0]}-01-01", "end_date": f"{years[-1]}-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum,snowfall_sum",
        "temperature_unit": "fahrenheit", "precipitation_unit": "inch", "timezone": "auto"})
    d = get_json("https://archive-api.open-meteo.com/v1/archive?" + q)["daily"]
    hi, lo, rain, snow = ([[] for _ in range(12)] for _ in range(4))
    totals = {}  # (year, month) -> [rain, snow]
    for t, mx, mn, r, s in zip(d["time"], d["temperature_2m_max"], d["temperature_2m_min"], d["rain_sum"], d["snowfall_sum"]):
        y, m = int(t[:4]), int(t[5:7]) - 1
        if mx is not None: hi[m].append(mx)
        if mn is not None: lo[m].append(mn)
        tot = totals.setdefault((y, m), [0.0, 0.0])
        tot[0] += r or 0
        tot[1] += s or 0
    for (y, m), (r, s) in totals.items():
        rain[m].append(r)
        snow[m].append(s)
    avg = lambda a, nd: round(sum(a) / len(a), nd) if a else None
    return {"hi": [avg(a, 1) for a in hi], "lo": [avg(a, 1) for a in lo],
            "rain": [avg(a, 2) for a in rain], "snow": [avg(a, 1) for a in snow]}


def main():
    this_year = dt.date.today().year
    years = list(range(this_year - YEARS_BACK, this_year))
    parks = load_parks()
    visits = fetch_visits(parks, years)
    weather = {}
    for p in parks:
        print("weather", p["id"], p["name"])
        weather[p["id"]] = fetch_weather(p, years)
        time.sleep(1.5)
    data = {
        "generated": dt.date.today().isoformat(),
        "years": years,
        "units": {"temp": "°F", "rain": "in", "snow": "in"},
        "sources": {"visits": "NPS Visitor Use Statistics, recreation visits",
                    "weather": "Open-Meteo historical weather archive (ERA5)"},
        "parks": {p["id"]: {"visits": visits[p["id"]], "wx": weather[p["id"]]} for p in parks},
    }
    out = ROOT / "data" / "park-history.js"
    out.parent.mkdir(exist_ok=True)
    out.write_text("// Generated by scripts/fetch_history.py. Do not edit by hand.\nwindow.PARK_HISTORY = "
                   + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
