"""Temporary debug of preliminary visits for some parks (one at a time)."""
import html, re, sys, urllib.request, http.cookiejar
sys.path.insert(0, "scripts")
import fetch_history as fh

for code in ["ACAD", "CAVE", "CHIR"]:
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    r = op.open(fh.YTD_REPORT.format(code=code), timeout=60); outer = r.read().decode("utf-8", "ignore")
    m = re.search(r'src="([^"]+)"', outer)
    print("==", code, "outer", len(outer), "iframe", bool(m))
    if not m: print(outer[:500]); continue
    r = op.open(fh.IRMA + html.unescape(m.group(1)), timeout=90); page = r.read().decode("utf-8", "ignore")
    print("  viewer url", r.geturl()[:200], "size", len(page))
    f = fh._ReportForm(); f.feed(page)
    for k, opts in f.selects.items():
        sel = re.search(r'name="' + re.escape(k) + r'".*?<option selected="selected" value="([^"]*)">([^<]*)', page, re.S)
        print("  select", k, len(opts), [t.replace("\xa0", " ").strip() for _, t in opts[:4]], "selected:", sel.groups() if sel else None)
    try:
        print("  result:", fh.fetch_prelim_visits(code, ["2026-09", "2026-10"]))
    except Exception as e:
        print("  error:", e)
