"""Temporary debug: the visit rows of the report for some parks, one at a time (July 2026)."""
import html, http.cookiejar, re, sys, time, urllib.request
sys.path.insert(0, "scripts")
import fetch_history as fh
for code in ["YOSE", "OLYM", "DENA", "VOYA", "ROMO", "JOTR", "GRCA"]:
    try:
        jar = http.cookiejar.CookieJar()
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)); op.addheaders = [("User-Agent", "Mozilla/5.0")]
        outer = op.open(fh.YTD_REPORT.format(code=code), timeout=60).read().decode()
        page = op.open(fh.IRMA + html.unescape(re.search(r'src="([^"]+)"', outer).group(1)), timeout=90).read().decode("utf-8", "ignore")
        f = fh._ReportForm(); f.feed(page)
        park = next(k for k, o in f.selects.items() if len(o) > 100)
        print("==", code, "selected park:", fh._sel_value(page, park), [t.replace("\xa0", " ").strip() for v, t in f.selects[park] if v == fh._sel_value(page, park)])
        if code == "GRCA":
            print("  grand options:", [t.replace("\xa0", " ").strip() for v, t in f.selects[park] if "Grand" in t]); continue
        e = re.search(r'"ExportUrlBase":"([^"]*)"', page).group(1).replace("\\u0026", "&")
        csv = op.open(fh.IRMA + e + "CSV", timeout=90).read().decode("utf-8-sig", "ignore")
        print("  " + "\n  ".join(l for l in csv.splitlines() if re.search(r"total|recreation", l, re.I))[:3000])
    except Exception as ex:
        print("==", code, "error", ex)
    time.sleep(3)
