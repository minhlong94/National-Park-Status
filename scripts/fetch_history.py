#!/usr/bin/env python3
"""Keep data/park-history.js: monthly visits and monthly weather for each park.

Visits:  NPS Visitor Use Statistics (irmaservices.nps.gov), recreation visits per month.
Weather: Open-Meteo historical archive (archive-api.open-meteo.com). For each month:
         the mean of the daily high, the mean of the daily low, the total rain and the total snow.

The file stores every month from FIRST_MONTH to the last month with data. Old months do not
change, so the script only adds new months:

1. A month is a candidate only after it ends (October is a candidate from November 1).
2. The script gets the candidate month for the first park only.
   If the visits or the weather of the first park are not available yet, the script stops.
   It does not request data for the other parks, and the file does not change.
3. If the first park has data, the script gets that month for all parks and adds it.

Preliminary visits of the current year (R63): the statistics service (irmaservices) has only final years.
NPS finalizes a year in the first quarter of the next year. Until then, the script reads the monthly
total from the IRMA report "Park YTD Version 1" (CSV export, one park and one month for each request).
The key "prelim" in the file is the first month with preliminary visits. On each run, the script asks the
statistics service for these months again. When a month is final, the script writes the final value.

The park list (id, code, lat, lon) comes from index.html. Standard library only.
Run: python3 scripts/fetch_history.py
"""
import calendar
import concurrent.futures
import csv
import datetime as dt
import io
import html as htmllib
import http.cookiejar
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "park-history.js"
FIRST_MONTH = "2023-01"     # the first month in the file
SOCKET_TIMEOUT = 20         # seconds for each network step: connect, TLS handshake, each read
TRIES = 3                   # tries for each request
SCRIPT_DEADLINE = 45 * 60   # seconds for the whole script (the first run of a year reads about 10 months for each park)
MAX_FAILS_IN_A_ROW = 3      # stop using a host after this many parks fail one after the other
# NPS Visitor Use Statistics reports Sequoia and Kings Canyon as separate units.
EXPECTED_PARKS = 64  # 63 until 2026; Chiricahua became the 64th national park (R47)
STATS_CODE = {"seki": "SEQU", "kica": "KICA"}
IRMA = "https://irma.nps.gov"
YTD_REPORT = IRMA + "/Stats/SSRSReports/Park%20Specific%20Reports/Park%20YTD%20Version%201?Park={code}"
PRELIM_WORKERS = 3          # parks that the script reads from the IRMA report at the same time (more gives 504 errors)
START = time.monotonic()


class DeadlineExceeded(Exception):
    pass


def time_left():
    left = SCRIPT_DEADLINE - (time.monotonic() - START)
    if left <= 0:
        raise DeadlineExceeded(f"script deadline of {SCRIPT_DEADLINE} s reached")
    return left


def get_json(url):
    """GET a JSON document with a socket timeout and a limited number of tries."""
    print("GET", url, flush=True)
    last = None
    for i in range(TRIES):
        t0 = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "National-Park-Status data script"})
            # The timeout applies to each socket operation: connect, TLS handshake and each read.
            with urllib.request.urlopen(req, timeout=min(SOCKET_TIMEOUT, time_left())) as r:
                body = r.read()
            print(f"  {len(body)} bytes in {time.monotonic() - t0:.1f} s", flush=True)
            return json.loads(body.decode("utf-8"))
        except DeadlineExceeded:
            raise
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ValueError) as e:
            last = e
            print(f"  try {i + 1} of {TRIES} failed after {time.monotonic() - t0:.1f} s: {e}", flush=True)
            if i < TRIES - 1:
                time.sleep(min(2 * 2 ** i, time_left()))
    raise RuntimeError(f"{url} failed {TRIES} times: {last}")


# ---- months ----
def ym(s):
    return int(s[:4]), int(s[5:7])


def ym_str(y, m):
    return f"{y:04d}-{m:02d}"


def add_months(s, n):
    y, m = ym(s)
    k = y * 12 + (m - 1) + n
    return ym_str(k // 12, k % 12 + 1)


def months_between(a, b):
    """Number of months from a to b (b - a)."""
    (ya, ma), (yb, mb) = ym(a), ym(b)
    return (yb - ya) * 12 + (mb - ma)


def last_complete_month(today):
    return add_months(ym_str(today.year, today.month), -1)


# ---- inputs ----
def load_parks():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parks = []
    for m in re.finditer(r'\{r:(\d+), code:"(\w+)",(?: id:"(\w+)",)? name:"([^"]+)".*?lat:(-?[\d.]+), lon:(-?[\d.]+)', html):
        r, code, pid, name, lat, lon = m.groups()
        parks.append({"id": pid or code, "code": code, "name": name, "lat": float(lat), "lon": float(lon)})
    if len(parks) != EXPECTED_PARKS:
        sys.exit(f"Expected {EXPECTED_PARKS} parks in index.html, found {len(parks)}")
    return parks


def load_store():
    """Read the data file. Returns None if there is no file or the file has an old format."""
    if not OUT.exists():
        return None
    m = re.search(r"window\.PARK_HISTORY = (\{.*\});", OUT.read_text(encoding="utf-8"), re.S)
    data = json.loads(m.group(1)) if m else None
    if not data or data.get("format") != 2:
        return None
    return data


def save_store(data):
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("// Generated by scripts/fetch_history.py. Do not edit by hand.\n"
                   "// Each array has one value for each month from \"first\" to \"last\".\n"
                   "window.PARK_HISTORY = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n",
                   encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes", flush=True)


# ---- sources ----
def stats_code(p):
    return STATS_CODE.get(p["id"], p["id"].upper())


def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for v in payload.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return []


def fetch_visits(codes, start, end):
    """Returns {UNITCODE: {"YYYY-MM": visits or None}} for the months from start to end."""
    (ys, ms), (ye, me) = ym(start), ym(end)
    out = {}
    for i in range(0, len(codes), 20):
        batch = codes[i:i + 20]
        q = urllib.parse.urlencode({"unitCodes": ",".join(batch), "startMonth": ms, "startYear": ys,
                                    "endMonth": me, "endYear": ye})
        for rec in records(get_json("https://irmaservices.nps.gov/v3/rest/stats/visitation?" + q)):
            if not {"UnitCode", "Year", "Month", "RecreationVisitors"} <= rec.keys():
                raise RuntimeError(f"Visitor statistics: unknown fields {list(rec)}")
            v = rec["RecreationVisitors"]
            out.setdefault(rec["UnitCode"].upper(), {})[ym_str(int(rec["Year"]), int(rec["Month"]))] = None if v is None else int(v)
        time.sleep(1)
    return out


# ---- preliminary visits of the current year (R63) ----
class _ReportForm(HTMLParser):
    """The form fields and the drop-down lists of the IRMA report viewer page."""
    def __init__(self):
        super().__init__()
        self.fields, self.selects, self._cur = {}, {}, None

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "input" and a.get("name") and a.get("type", "text") in ("hidden", "text"):
            self.fields[a["name"]] = a.get("value") or ""
        elif tag == "select" and a.get("name"):
            self._cur = a["name"]
            self.selects[self._cur] = []
        elif tag == "option" and self._cur:
            self.selects[self._cur].append([a.get("value"), ""])

    def handle_data(self, d):
        if self._cur and self.selects[self._cur]:
            self.selects[self._cur][-1][1] += d

    def handle_endtag(self, tag):
        if tag == "select":
            self._cur = None


def _month_label(mon):
    y, m = ym(mon)
    return f"{calendar.month_abbr[m]} {y}"


def _sel_value(page, name):
    """The selected value of a drop-down list in the viewer page."""
    m = re.search(r'name="' + re.escape(name) + r'".*?<option selected="selected" value="([^"]*)"', page, re.S)
    return m.group(1) if m else None


def _num(cell):
    cell = (cell or "").replace(",", "").strip()
    return int(cell) if cell.isdigit() else None


def pick_total(csv_text, prev=None):
    """The park total "ThisMonth" from the CSV of the report, or None. Returns (value, label, rows).

    The rows are different in each park:
    1. A named total row: "Total Adjusted Recreation Visits" (Great Smoky Mountains), "Total Recreation Visitors"
       (Acadia, Olympic), "Recreation Visitors" (Joshua Tree). Some parks also have a "Total Recreation Visits"
       row for each entrance (Yosemite), so the script takes the largest. Rows such as "Total Recreation Hours"
       or "Non-Recreation Visits" do not count.
    2. Else, the row whose "SameMonthLastYear" is the final value of last year (prev, from the data file),
       for example "Canyonlands NP Visitors" or "NPS Recreation Visits" (Redwood).
    """
    rows = []
    for r in csv.reader(io.StringIO(csv_text)):
        if len(r) >= 4 and _num(r[2]) is not None:
            rows.append((r[0], re.sub(r"\s+", " ", r[1]).strip(), _num(r[2]), _num(r[3])))
    named = [x for x in rows if re.fullmatch(r"(Total )?(Adjusted )?Recreation Visit(s|ors)", x[1], re.I)]
    if named:
        best = max(named, key=lambda x: x[2])
        return best[2], f"{best[0]} / {best[1]}", rows
    if prev:
        same = [x for x in rows if x[3] is not None and abs(x[3] - prev) <= max(1, prev * 0.005)
                and re.search(r"visit", x[1], re.I) and not re.search(r"non|hour", x[1], re.I)]
        if same:
            best = max(same, key=lambda x: x[2])
            return best[2], f"{best[0]} / {best[1]} (same last year)", rows
    return None, None, rows


def fetch_prelim_visits(code, months, name=None, debug=False, prev=None):
    """Returns {"YYYY-MM": visits or None} from the IRMA report "Park YTD Version 1".

    The report shows one month. The park comes from the URL. The script selects each month in the
    form of the report viewer (an ASP.NET postback, as a browser does), then exports the report as CSV.
    It uses the row "Total Adjusted Recreation Visits", column "ThisMonth".
    """
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "Mozilla/5.0 (National-Park-Status data script)")]

    def get(url, data=None):
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        for k in range(TRIES):
            try:
                time.sleep(0.3)  # be gentle with the IRMA server
                with op.open(urllib.request.Request(url, data=body), timeout=min(60, time_left())) as r:
                    return r.geturl(), r.read().decode("utf-8-sig", "ignore")
            except DeadlineExceeded:
                raise
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
                # 502, 503, 504 and 403 come when the server is busy: wait and try again
                if k == TRIES - 1 or (isinstance(e, urllib.error.HTTPError) and e.code not in (403, 429, 500, 502, 503, 504)):
                    raise
                time.sleep(5 * (k + 1))

    _, outer = get(YTD_REPORT.format(code=code))
    m = re.search(r'src="([^"]+)"', outer)
    if not m:
        raise RuntimeError(f"{code}: the report page has no viewer")
    url, page = get(IRMA + htmllib.unescape(m.group(1)))
    form = _ReportForm()
    form.feed(page)
    park_sel = next((k for k, opts in form.selects.items() if len(opts) > 100), None)
    if park_sel and _sel_value(page, park_sel) in (None, "0") and name:
        # Some codes (for example CAVE) do not select the park. Select it by name, as a browser does.
        label = lambda t: t.replace("\xa0", " ").strip()
        cands = [(v, label(t)) for v, t in form.selects[park_sel] if re.match(re.escape(name) + r" (NP|National Park)\b", label(t))]
        if not cands:
            # Some parks (for example Carlsbad Caverns, Chiricahua) are not in this report. Their months stay blank.
            print(f"  {code}: not in the report. Its preliminary months stay blank.", flush=True)
            return {mon: None for mon in months}
        data = dict(form.fields)
        data.update({park_sel: cands[0][0], "__EVENTTARGET": park_sel, "__EVENTARGUMENT": ""})
        url, page = get(url, data)
        if debug:
            print(f"  {code}: selected {cands[0][1]} by name", flush=True)
    out = {}
    for mon in months:
        form = _ReportForm()
        form.feed(page)
        label = _month_label(mon)
        mon_sel = next((k for k, opts in form.selects.items()
                        if any(re.fullmatch(r"[A-Z][a-z]{2} \d{4}", t.replace("\xa0", " ").strip()) for _, t in opts)), None)
        if not mon_sel:
            print(f"  {code}: the report has no month list. Its preliminary months stay blank.", flush=True)
            return {mon: None for mon in months}
        value = next((v for v, t in form.selects[mon_sel] if t.replace("\xa0", " ").strip() == label), None)
        if value is None:
            out[mon] = None  # NPS has no report for this month yet
            continue
        data = dict(form.fields)
        for k, opts in form.selects.items():
            if k != mon_sel and opts and _sel_value(page, k) is not None:
                data[k] = _sel_value(page, k)
        data.update({mon_sel: value, "ReportViewer$ctl04$ctl00": "View Report", "__EVENTTARGET": "", "__EVENTARGUMENT": ""})
        url, page = get(url, data)
        e = re.search(r'"ExportUrlBase":"([^"]*)"', page)
        if not e:
            raise RuntimeError(f"{code} {mon}: no export link")
        _, csv_text = get(IRMA + e.group(1).replace("\\u0026", "&") + "CSV")
        if f"Report Date: {label}" not in csv_text:
            raise RuntimeError(f"{code} {mon}: the report is for another month")
        p_mon = (prev or {}).get(mon)
        value, label_used, rows = pick_total(csv_text, p_mon)
        out[mon] = value
        if value is None or debug:
            # Some parks (for example Yellowstone) report only overnight stays in this report
            print(f"  {code} {mon}: {'no total row' if value is None else 'row ' + repr(label_used)}; last year {p_mon}; "
                  f"rows: {[(g[:25], l[:40], tm, ly) for g, l, tm, ly in rows if re.search('recreation|visit', g + l, re.I)][:8]}", flush=True)
    return out


def fetch_prelim_all(codes, months, names, prevs):
    """Preliminary visits for many parks, PRELIM_WORKERS at the same time. Each park gets 3 tries."""
    def one(code):
        last = None
        for k in range(TRIES):
            try:
                return code, fetch_prelim_visits(code, months, names.get(code), prev=prevs.get(code))
            except DeadlineExceeded:
                raise
            except Exception as e:  # noqa: BLE001
                last = e
                print(f"  retry {k + 1} {code}: {e}", flush=True)
                time.sleep(3 * (k + 1))
        raise RuntimeError(f"preliminary visits {code}: {last}")
    print(f"Preliminary visits for {len(codes)} parks, {months[0]} to {months[-1]}.", flush=True)
    out = {}
    with concurrent.futures.ThreadPoolExecutor(PRELIM_WORKERS) as ex:
        for code, vals in ex.map(one, codes):
            out[code] = vals
            print(f"  {code}: {vals}", flush=True)
    return out


def fetch_weather(p, start, end):
    """Returns {"YYYY-MM": {"hi", "lo", "rain", "snow"} or None}. None means a month with missing days."""
    last_day = calendar.monthrange(*ym(end))[1]
    q = urllib.parse.urlencode({
        "latitude": p["lat"], "longitude": p["lon"],
        "start_date": f"{start}-01", "end_date": f"{end}-{last_day:02d}",
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum,snowfall_sum",
        "temperature_unit": "fahrenheit", "precipitation_unit": "inch", "timezone": "auto"})
    d = get_json("https://archive-api.open-meteo.com/v1/archive?" + q).get("daily") or {}
    days = {}
    for t, mx, mn, r, s in zip(d.get("time", []), d.get("temperature_2m_max", []), d.get("temperature_2m_min", []),
                               d.get("rain_sum", []), d.get("snowfall_sum", [])):
        days.setdefault(t[:7], []).append((mx, mn, r, s))
    out = {}
    n = months_between(start, end) + 1
    for k in range(n):
        mon = add_months(start, k)
        rows = days.get(mon, [])
        complete = len(rows) == calendar.monthrange(*ym(mon))[1] and all(None not in row for row in rows)
        if not complete:
            out[mon] = None
            continue
        out[mon] = {"hi": round(sum(r[0] for r in rows) / len(rows), 1),
                    "lo": round(sum(r[1] for r in rows) / len(rows), 1),
                    "rain": round(sum(r[2] for r in rows), 2),
                    "snow": round(sum(r[3] for r in rows), 1)}
    return out


# ---- main ----
def backfill_new_parks(store, parks):
    """A park that is new in index.html (for example Chiricahua, R47) gets all the months that the file has.
    The other parks do not change. If a request fails, the new park is not added, and the next run tries again."""
    new = [p for p in parks if p["id"] not in store["parks"]]
    if not new:
        return False
    months = [add_months(store["first"], k) for k in range(months_between(store["first"], store["last"]) + 1)]
    print(f"New parks: {[p['id'] for p in new]}. Getting {store['first']} to {store['last']} for them.", flush=True)
    visits = fetch_visits(sorted({stats_code(p) for p in new}), store["first"], store["last"])
    for p in new:
        try:
            w = fetch_weather(p, store["first"], store["last"])
        except Exception as e:  # noqa: BLE001
            print(f"ERROR weather {p['id']}: {e}. The park is not added now.", flush=True)
            continue
        pv = visits.get(stats_code(p), {})
        rec = {"v": [], "hi": [], "lo": [], "rain": [], "snow": []}
        for mon in months:
            rec["v"].append(pv.get(mon))
            for key in ("hi", "lo", "rain", "snow"):
                rec[key].append((w.get(mon) or {}).get(key))
        store["parks"][p["id"]] = rec
    return True


def finalize_prelim(store, parks):
    """Replace preliminary visits with the final values when the statistics service has them (R63)."""
    pre = store.get("prelim")
    if not pre:
        return False
    code1 = stats_code(parks[0])
    v1 = fetch_visits([code1], pre, store["last"]).get(code1, {})
    k = 0
    while months_between(add_months(pre, k), store["last"]) >= 0 and v1.get(add_months(pre, k)) is not None:
        k += 1
    if k == 0:
        print(f"Visits from {pre} are still preliminary.", flush=True)
        return False
    end = add_months(pre, k - 1)
    print(f"Final visits are available for {pre} to {end}. The script replaces the preliminary values.", flush=True)
    visits = fetch_visits(sorted({stats_code(p) for p in parks}), pre, end)
    for p in parks:
        rec = store["parks"].get(p["id"])
        pv = visits.get(stats_code(p), {})
        for j in range(k):
            mon = add_months(pre, j)
            if rec and pv.get(mon) is not None:
                rec["v"][months_between(store["first"], mon)] = pv[mon]
    nxt = add_months(end, 1)
    if months_between(nxt, store["last"]) >= 0:
        store["prelim"] = nxt
    else:
        store.pop("prelim", None)
    return True


def main():
    today = dt.date.today()
    parks = load_parks()
    store = load_store()
    if store is not None and backfill_new_parks(store, parks):
        save_store(store)
    if store is not None and finalize_prelim(store, parks):
        save_store(store)
    target = last_complete_month(today)  # the newest month that has ended

    if store is None:
        print(f"No data file in the current format. Getting all months from {FIRST_MONTH}.", flush=True)
        start = FIRST_MONTH
    else:
        start = add_months(store["last"], 1)
    if months_between(start, target) < 0:
        print(f"The file has data to {store['last']}. The next month, {start}, has not ended. Nothing to do.")
        return

    # Step 1: the first park only. Find the newest month that has visits and complete weather.
    first = parks[0]
    print(f"Checking {start} to {target} for the first park, {first['name']}.", flush=True)
    code1 = stats_code(first)
    v1 = fetch_visits([code1], start, target).get(code1, {})
    w1 = fetch_weather(first, start, target)
    cand = [add_months(start, k) for k in range(months_between(start, target) + 1)]
    # Months that the statistics service does not have yet: try the preliminary report (R63)
    missing = [mon for mon in cand if v1.get(mon) is None]
    def prev_year(p):
        """The final visits of the same month one year before, from the data file: the check of the report row."""
        rec = (store or {}).get("parks", {}).get(p["id"])
        out = {}
        for mon in cand:
            k = months_between(store["first"], add_months(mon, -12)) if store else -1
            out[mon] = rec["v"][k] if rec and 0 <= k < len(rec["v"]) else None
        return out
    p1 = fetch_prelim_visits(code1, missing, first["name"], prev=prev_year(first)) if missing else {}
    end, prelim_months = None, []
    for mon in cand:
        vis = v1.get(mon) if v1.get(mon) is not None else p1.get(mon)
        if vis is None or w1.get(mon) is None:
            print(f"The first park has no {'visits' if vis is None else 'complete weather'} for {mon}. "
                  f"The script stops here and does not request data for the other parks.", flush=True)
            break
        if v1.get(mon) is None:
            prelim_months.append(mon)
        end = mon
    if end is None:
        print("No new data. The data file did not change.")
        return
    print(f"New months: {start} to {end}. Getting them for all parks.", flush=True)

    # Step 2: all parks, new months only.
    codes = sorted({stats_code(p) for p in parks})
    visits = fetch_visits(codes, start, end)
    errors = []
    if prelim_months:
        try:
            names = {stats_code(p): {"seki": "Sequoia", "kica": "Kings Canyon"}.get(p["id"], p["name"]) for p in parks}
            prevs = {stats_code(p): prev_year(p) for p in parks}
            pv = fetch_prelim_all([c for c in codes if c != code1], prelim_months, names, prevs)
            pv[code1] = p1
            for c in codes:
                for mon in prelim_months:
                    if visits.get(c, {}).get(mon) is None:
                        visits.setdefault(c, {})[mon] = pv.get(c, {}).get(mon)
        except Exception as e:  # noqa: BLE001
            # Do not add months with holes. The next run tries the same months again.
            sys.exit(f"Preliminary visits failed. The data file did not change.\n{e}")
    weather, fails_in_a_row = {}, 0
    for p in parks:
        if p is first:
            weather[p["id"]] = w1
            continue
        print("weather", p["id"], p["name"], flush=True)
        try:
            weather[p["id"]] = fetch_weather(p, start, end)
            fails_in_a_row = 0
        except DeadlineExceeded as e:
            errors.append(f"weather: {e}")
            break
        except Exception as e:
            errors.append(f"weather {p['id']}: {e}")
            print(f"ERROR weather {p['id']}:", e, flush=True)
            fails_in_a_row += 1
            if fails_in_a_row >= MAX_FAILS_IN_A_ROW:
                errors.append(f"weather: stopped after {fails_in_a_row} parks failed one after the other")
                break
        time.sleep(0.5)
    if errors:
        # Do not add months with holes. The next run tries the same months again.
        sys.exit("Weather failed. The data file did not change.\n" + "\n".join(errors[:20]))

    # Step 3: add the new months.
    new_months = [add_months(start, k) for k in range(months_between(start, end) + 1)]
    if store is None:
        store = {"format": 2, "first": FIRST_MONTH, "last": None, "parks": {}}
    for p in parks:
        rec = store["parks"].setdefault(p["id"], {"v": [], "hi": [], "lo": [], "rain": [], "snow": []})
        pv = visits.get(stats_code(p), {})
        for mon in new_months:
            w = weather[p["id"]].get(mon) or {}
            rec["v"].append(pv.get(mon))
            for key in ("hi", "lo", "rain", "snow"):
                rec[key].append(w.get(key))
    store["last"] = end
    if prelim_months and not store.get("prelim"):
        store["prelim"] = prelim_months[0]
    store["updated"] = today.isoformat()
    store["sources"] = {"visits": "NPS Visitor Use Statistics, recreation visits (months from \"prelim\" are preliminary: IRMA report Park YTD Version 1)",
                        "weather": "Open-Meteo historical weather archive (ERA5)"}
    save_store(store)


if __name__ == "__main__":
    main()
