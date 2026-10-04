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
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS_BACK = 3
SOCKET_TIMEOUT = 30       # seconds for each network step: connect, TLS handshake, each read
TRIES = 3                 # tries for each request
SCRIPT_DEADLINE = 10 * 60 # seconds for the whole script
MAX_FAILS_IN_A_ROW = 3    # stop using a host after this many parks fail one after the other
START = time.monotonic()


class DeadlineExceeded(Exception):
    pass


def time_left():
    left = SCRIPT_DEADLINE - (time.monotonic() - START)
    if left <= 0:
        raise DeadlineExceeded(f"script deadline of {SCRIPT_DEADLINE} s reached")
    return left
# NPS Visitor Use Statistics reports Sequoia and Kings Canyon as separate units.
STATS_CODE = {"seki": "SEQU", "kica": "KICA"}


def get_json(url):
    """GET a JSON document with a connect timeout, a read timeout and a limited number of tries."""
    last = None
    for i in range(TRIES):
        timeout = min(SOCKET_TIMEOUT, time_left())
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "National-Park-Status data script"})
            # The timeout applies to each socket operation: connect, TLS handshake and each read.
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            print(f"  {len(body)} bytes in {time.monotonic() - t0:.1f} s", flush=True)
            return json.loads(body.decode("utf-8"))
        except DeadlineExceeded:
            raise
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ValueError) as e:
            last = e
            print(f"  try {i + 1} of {TRIES} failed after {time.monotonic() - t0:.1f} s: {e}", flush=True)
            if i < TRIES - 1:
                time.sleep(min(3 * 2 ** i, time_left()))
    raise RuntimeError(f"{url} failed {TRIES} times: {last}")


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
        print("GET", url, flush=True)
        recs = records(get_json(url))
        if not recs:
            raise RuntimeError("Visitor statistics: empty response")
        if i == 0:
            print("  sample record:", json.dumps(recs[0])[:400])
        k_unit = find_key(recs[0], r"unit_?code")
        k_year = find_key(recs[0], r"year")
        k_month = find_key(recs[0], r"month")
        k_vis = find_key(recs[0], r"recreation_?visit(or)?s?")
        if not all([k_unit, k_year, k_month, k_vis]):
            raise RuntimeError(f"Visitor statistics: unknown fields {list(recs[0])}")
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
    url = "https://archive-api.open-meteo.com/v1/archive?" + q
    print("GET", url, flush=True)
    d = get_json(url)["daily"]
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


def load_previous():
    """Read the last good data file, so that one failed source does not delete good data."""
    f = ROOT / "data" / "park-history.js"
    if not f.exists():
        return None
    m = re.search(r"window\.PARK_HISTORY = (\{.*\});", f.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1)) if m else None


def main():
    this_year = dt.date.today().year
    years = list(range(this_year - YEARS_BACK, this_year))
    parks = load_parks()
    prev = load_previous()
    prev_ok = prev is not None and prev.get("years") == years
    errors = []

    try:
        visits = fetch_visits(parks, years)
    except Exception as e:
        errors.append(f"visits: {e}")
        print("ERROR visits:", e, flush=True)
        visits = {p["id"]: (prev["parks"][p["id"]]["visits"] if prev_ok and p["id"] in prev["parks"]
                            else {str(y): [None] * 12 for y in years}) for p in parks}

    weather = {}
    fails_in_a_row = 0
    for p in parks:
        print("weather", p["id"], p["name"], flush=True)
        try:
            weather[p["id"]] = fetch_weather(p, years)
            fails_in_a_row = 0
        except DeadlineExceeded as e:
            errors.append(f"weather: {e}")
            print("ERROR weather:", e, flush=True)
            break
        except Exception as e:
            errors.append(f"weather {p['id']}: {e}")
            print(f"ERROR weather {p['id']}:", e, flush=True)
            fails_in_a_row += 1
            if fails_in_a_row >= MAX_FAILS_IN_A_ROW:
                errors.append(f"weather: stopped after {fails_in_a_row} parks failed one after the other")
                print("ERROR weather: the host does not answer. The script stops the weather requests.", flush=True)
                break
        time.sleep(1)
    for p in parks:
        if p["id"] not in weather:
            weather[p["id"]] = (prev["parks"][p["id"]]["wx"] if prev_ok and p["id"] in prev["parks"]
                                else {"hi": [None] * 12, "lo": [None] * 12, "rain": [None] * 12, "snow": [None] * 12})

    has_visits = any(v is not None for p in visits.values() for y in p.values() for v in y)
    has_weather = any(v is not None for p in weather.values() for v in p["hi"])
    if not has_visits and not has_weather:
        sys.exit("No data from any source. The data file did not change.\n" + "\n".join(errors))
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
    print("wrote", out, out.stat().st_size, "bytes", flush=True)
    if errors:
        # The file keeps the good data, but the run must show that a source failed.
        sys.exit(f"{len(errors)} source errors:\n" + "\n".join(errors[:20]))


if __name__ == "__main__":
    main()
