#!/usr/bin/env python3
"""Build data/seasonal.js: seasonal closures of park facilities (R35).

Two sources:
1. NPS API (campgrounds and visitor centers): the "closed" exceptions of the operating hours.
   The script keeps the closures that end today or later, start in the next 12 months and are at least 7 days long.
   One-day closures (for example Christmas Day) are left out.
3. Park roads and hours pages: the planned road opening and closing dates of this year
   (for example Yellowstone and Grand Teton).
2. Park "seasonal" pages with history datasets (for example Yosemite): the open dates of each campground
   and trail in each year. The script finds the "Download This Dataset" links on the page and keeps the
   datasets with a "Year" column and date ranges such as "Jun 20-Sep 26".

The workflow .github/workflows/update-seasonal.yml runs this script each Monday.
Set the NPS_API_KEY environment variable to use your own key. Otherwise the script uses DEMO_KEY.
"""
import csv
import html
import datetime as dt
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_history as fh  # noqa: E402  (load_parks)

ROOT = fh.ROOT
OUT = ROOT / "data" / "seasonal.js"
API = "https://developer.nps.gov/api/v1"
KEY = os.environ.get("NPS_API_KEY") or "DEMO_KEY"
UA = {"User-Agent": "National-Park-Status (https://github.com/minhlong94/National-Park-Status)"}
PAGES = {"yose": "https://www.nps.gov/yose/planyourvisit/seasonal.htm",
         "grsm": "https://www.nps.gov/grsm/planyourvisit/seasonal.htm"}
HIST_YEARS = 10
MIN_DAYS = 7
MON = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def get(url, tries=4, timeout=90, raw=False):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                data = r.read()
                return data.decode("utf-8-sig", "ignore") if raw else json.loads(data)
        except Exception as e:  # noqa: BLE001
            print(f"  retry {k + 1}: {e} {url.split('api_key')[0][:120]}", flush=True)
            time.sleep(5 * (k + 1))
    raise RuntimeError("failed: " + url.split("api_key")[0])


def api_all(endpoint, codes):
    items, start = [], 0
    while True:
        j = get(f"{API}/{endpoint}?parkCode={','.join(codes)}&limit=500&start={start}&api_key={KEY}")
        items += j.get("data") or []
        start += len(j.get("data") or [])
        if not j.get("data") or start >= int(j.get("total") or 0):
            return items


def closures(items, kind, today):
    """The long "closed" exceptions of each item that end today or later."""
    out = {}
    horizon = (today + dt.timedelta(days=365)).isoformat()
    for d in items:
        seen = set()
        for oh in d.get("operatingHours") or []:
            for e in oh.get("exceptions") or []:
                hours = (e.get("exceptionHours") or {}).values()
                a, b = e.get("startDate") or "", e.get("endDate") or ""
                if not a or not b or not hours or any(v != "Closed" for v in hours):
                    continue
                if b < today.isoformat() or a > horizon:
                    continue
                days = (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days + 1
                if days < MIN_DAYS or (a, b) in seen:
                    continue
                seen.add((a, b))
                out.setdefault(d["parkCode"], []).append({"n": d.get("name", "").strip(), "k": kind, "from": a, "to": b,
                                                          "why": (e.get("name") or "").strip()})
    return out


def parse_range(cell, year):
    """'Jun 20-Sep 26', 'Aug 1-29', 'Apr 30-Jan 7, 2024' -> (open date, close date or None). None if no open date."""
    c = cell.strip().lower().replace("–", "-")
    m = re.match(r"^([a-z]{3})[a-z]*\.?\s*(\d{1,2})\s*-\s*(?:([a-z]{3})[a-z]*\.?\s*)?(\d{1,2})?(?:,\s*(\d{4}))?", c)
    if not m or m.group(1) not in MON:
        return None
    try:
        o = dt.date(year, MON[m.group(1)], int(m.group(2)))
        if not m.group(4):
            return o, None
        mon2 = MON.get(m.group(3) or m.group(1))
        y2 = int(m.group(5)) if m.group(5) else year
        cl = dt.date(y2, mon2, int(m.group(4)))
        if cl < o:
            cl = dt.date(year + 1, mon2, int(m.group(4)))
        return o, cl
    except ValueError:
        return None


def history(code, url, today):
    """Usual open dates of campgrounds and trails, from the datasets on a park seasonal page."""
    html = get(url, raw=True)
    links = sorted(set(re.findall(r'href="(/common/uploads/sortable_dataset/[^"]+\.csv[^"]*)"', html)))
    out = []
    for link in links:
        tail = link.split("?")[0].rsplit("-", 1)[-1].lower()  # for example "CopyCampgrounds.csv"
        kind = "trail" if "trail" in tail else "campground" if "campground" in tail else "facility"
        rows = list(csv.reader(io.StringIO(get("https://www.nps.gov" + link, raw=True))))
        if not rows or rows[0][0].strip().lower() != "year":
            continue
        names = [h.strip() for h in rows[0][1:]]
        for col, name in enumerate(names, start=1):
            if not name:
                continue
            seasons, closed_years = [], []
            for r in rows[1:]:
                ym = re.match(r"\s*(\d{4})", r[0] if r else "")
                if not ym or col >= len(r):
                    continue
                y = int(ym.group(1))
                if y < today.year - HIST_YEARS:
                    continue
                cell = r[col].strip()
                if re.search(r"did not open", cell, re.I):
                    closed_years.append(y)
                    continue
                pr = parse_range(cell, y)
                if pr:
                    seasons.append((y, pr[0], pr[1]))
            if len(seasons) < 3:  # not a dataset of date ranges
                continue
            od = [(o - dt.date(o.year, 1, 1)).days for _, o, _ in seasons]
            cd = [(c - dt.date(o.year, 1, 1)).days for _, o, c in seasons if c]
            last = max(seasons)
            out.append({"n": name, "k": kind, "o": round(statistics.median(od)),
                        "c": round(statistics.median(cd)) if cd else None, "years": len(seasons),
                        "noOpen": sorted(closed_years, reverse=True),
                        "last": [last[0], last[1].isoformat(), last[2].isoformat() if last[2] else None]})
        print(f"  {code}: {link.split('/')[-1][:60]} -> {sum(1 for x in out if x['k'] == kind)} {kind} items", flush=True)
    return out


def page_text(url):
    """The main text of an NPS page, with one line for each paragraph, list item or table row."""
    try:  # one try: most parks do not have the page
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
            s = r.read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"{url}: {e}")
    i = s.find('id="main"')
    s = s[i:] if i > 0 else s
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"</(p|li|tr|h\d|div)>|<br\s*/?>", "\n", s)
    s = re.sub(r"</t[dh]>", " | ", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    s = re.sub(r"[ \t]+", " ", s)
    return s.split("Park footer")[0]


def iso(mon, day, year):
    m = MON.get(mon[:3].lower())
    try:
        return dt.date(year, m, int(day)).isoformat() if m else None
    except ValueError:
        return None


def road_schedule(code, today):
    """Planned road opening and closing dates of this year (R43), from the park roads or hours page.

    Two forms on NPS pages:
    - "Open April 17 - October 31, 2026: West Entrance to Madison, Madison to Old Faithful" (Yellowstone)
    - "May 1, Spring opening of Teton Park Road" and "October 31, Winter closure of Teton Park Road" (Grand Teton)
    """
    for page in ("parkroads.htm", "hours.htm"):
        url = f"https://www.nps.gov/{code}/planyourvisit/{page}"
        try:
            t = page_text(url)
        except RuntimeError:
            continue
        i = t.find("Road Opening")  # start at the dates heading, if the page has one
        t = t[i:] if i >= 0 else t
        t = re.split(r"(?i)oversnow vehicle", t)[0]  # only the dates for regular vehicles
        ym = re.search(r"\b(20\d\d) Road Opening", t)
        year = int(ym.group(1)) if ym else today.year
        items = []
        for m in re.finditer(r"Open\s+(year-round|([A-Z][a-z]+)\.?\s+(\d{1,2})\s*[-–]\s*([A-Z][a-z]+)\.?\s+(\d{1,2})\*?,?\s*(20\d\d)?)\s*:\s*([^\n]+)", t):
            y = int(m.group(6)) if m.group(6) else year
            o = None if m.group(1) == "year-round" else iso(m.group(2), m.group(3), y)
            c = None if m.group(1) == "year-round" else iso(m.group(4), m.group(5), y)
            if m.group(1) != "year-round" and not (o and c):
                continue
            for seg in re.split(r",\s*(?![^(]*\))", m.group(7).split(". ")[0]):
                seg = seg.strip(" .*")
                if 3 < len(seg) < 90:
                    items.append({"n": seg, "open": o, "close": c})
        pairs = {}
        for m in re.finditer(r"([A-Z][a-z]+)\.?\s+(\d{1,2}),?\s*\|?\s*(?:Spring |Summer |Seasonal )?(opening|Winter closure|closure|closing) of ([A-Z][^|\n.,]{3,60})", t):
            d = iso(m.group(1), m.group(2), year)
            road = m.group(4).strip()
            if d:
                pairs.setdefault(road, {})["open" if "open" in m.group(3).lower() else "close"] = d
        items += [{"n": r, "open": v["open"], "close": v["close"]} for r, v in pairs.items() if v.get("open") and v.get("close")]
        if items:
            print(f"  roads {code}: {len(items)} from {page}", flush=True)
            return {"year": year, "src": url, "items": items}
    return None


# ---- Seasonal area closures (R44): wildlife closures, area and trail closures with yearly dates ----
AREA_PAGES = ["planyourvisit/hours.htm", "planyourvisit/conditions.htm", "planyourvisit/seasonal.htm", "planyourvisit/closures.htm",
              "planyourvisit/wildlife-closures.htm", "learn/management/wildlife-closures.htm", "learn/management/closures.htm",
              "learn/management/compendium.htm", "learn/management/superintendents-compendium.htm"]
MONTHS_RX = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?"
RANGE_RX = re.compile(MONTHS_RX + r"\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*20\d\d)?\)?\s*(?:through|thru|to|until|-|–|—)\s*" + MONTHS_RX + r"\s+(\d{1,2})(?:st|nd|rd|th)?", re.I)
CLOSED_RX = re.compile(r"\b(closed|closure|closures|no (public )?entry|prohibited|off.limits|avoid)\b", re.I)


def page_html(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as r:
            if r.geturl().rstrip("/").endswith("/index.htm") and not url.endswith("index.htm"):
                return None, None  # NPS sends a missing page to the park home page
            return r.read(), r.headers.get("Content-Type", "")
    except Exception:  # noqa: BLE001
        return None, None


def html_to_text(s):
    i = s.find('id="main"')
    s = s[i:] if i > 0 else s
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<h[1-4][^>]*>", "\n## ", s)  # keep the headings: a "Seasonal Closures" heading covers the list below it
    s = re.sub(r"</(p|li|tr|h\d|div)>|<br\s*/?>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"[ \t\xa0]+", " ", s).split("Park footer")[0]


def pdf_to_text(data):
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data); f.flush()
        try:
            return subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, timeout=60).stdout.decode("utf-8", "ignore")
        except Exception:  # noqa: BLE001
            return ""


def closure_sentences(text):
    """Sentences that close something between two dates of each year."""
    text = re.sub(r"-\n\s*", "", text)          # words split at the end of a PDF line
    text = re.sub(r"\s*\n\s*(?=[a-z(])", " ", text)  # join lines of one sentence
    out, heading = [], ""
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip(" •·-*")
        if line.startswith("##"):
            heading = line
            continue
        for sent in re.split(r"(?<=[.;])\s+", line):
            if not (25 <= len(sent) <= 600) or not (CLOSED_RX.search(sent) or CLOSED_RX.search(line) or re.search(r"(?i)closure", heading)):
                continue
            t = line if len(line) <= 400 else sent  # a short list item stays whole, so its subject stays with the dates
            for m in RANGE_RX.finditer(sent):
                a, b = MON.get(m.group(1)[:3].lower()), MON.get(m.group(3)[:3].lower())
                if a and b and 1 <= int(m.group(2)) <= 31 and 1 <= int(m.group(4)) <= 31:
                    out.append({"t": t, "from": f"{a:02d}-{int(m.group(2)):02d}", "to": f"{b:02d}-{int(m.group(4)):02d}",
                                "vol": bool(re.search(r"(?i)voluntar", t))})
    return out


def area_closures(code):
    """Seasonal closures with yearly dates from the park pages and the Superintendent's Compendium (also PDF)."""
    base = f"https://www.nps.gov/{code}/"
    todo, seen, found = [base + p for p in AREA_PAGES], set(), []
    while todo and len(seen) < 16:
        url = todo.pop(0)
        if url in seen:
            continue
        seen.add(url)
        data, ctype = page_html(url)
        if not data:
            continue
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            text = pdf_to_text(data)
        else:
            s = data.decode("utf-8", "ignore")
            text = html_to_text(s)
            # follow links about closures or the compendium, in this park (one level)
            if url in [base + p for p in AREA_PAGES]:
                for href, label in re.findall(r'href="([^"#]+)"[^>]*>(.*?)</a>', s, flags=re.S):
                    if re.search(r"(?i)closure|compendium", href + " " + label):
                        u = href if href.startswith("http") else "https://www.nps.gov" + href if href.startswith("/") else None
                        if u and (u.startswith(base) or "/common/uploads/" in u or u.startswith("https://www.nps.gov/" + code)) and u not in seen:
                            todo.append(u)
        for c in closure_sentences(text):
            c["src"] = url
            found.append(c)
    # one entry for each sentence and date range
    out, keys = [], set()
    for c in found:
        k = (c["t"][:80].lower(), c["from"], c["to"])
        if k not in keys:
            keys.add(k); out.append(c)
    return out[:40]


def main():
    today = dt.date.today()
    parks = fh.load_parks()
    codes = sorted({p["code"] for p in parks})
    data = {"built": today.isoformat(), "parks": {}}
    ok = False
    for endpoint, kind in (("campgrounds", "campground"), ("visitorcenters", "visitor center")):
        try:
            items = api_all(endpoint, codes)
        except RuntimeError as e:
            print("NPS API failed:", endpoint, e, flush=True)
            continue
        ok = True
        found = closures(items, kind, today)
        print(f"{endpoint}: {len(items)} items, closures in {len(found)} parks", flush=True)
        for code, lst in found.items():
            data["parks"].setdefault(code, {}).setdefault("closures", []).extend(lst)
    for code, url in PAGES.items():
        try:
            h = history(code, url, today)
        except RuntimeError as e:
            print("history failed:", code, e, flush=True)
            continue
        if h:
            data["parks"].setdefault(code, {})["history"] = h
            data["parks"][code]["page"] = url
    for code in codes:
        ac = area_closures(code)
        print(f"  areas {code}: {len(ac)}", flush=True)
        if ac:
            data["parks"].setdefault(code, {})["areas"] = ac
        rs = road_schedule(code, today)
        if rs:
            data["parks"].setdefault(code, {})["roads"] = rs
    if not ok:
        sys.exit("The NPS API did not answer. The file does not change.")
    for v in data["parks"].values():
        v.get("closures", []).sort(key=lambda x: (x["from"], x["n"]))
    OUT.write_text("// Generated by scripts/fetch_seasonal.py. Do not edit by hand.\n"
                   "// closures: k = kind, from/to = closed dates. history: o/c = median open/close day of the year (Jan 1 = 0).\n"
                   "window.PARK_SEASONAL = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n",
                   encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
