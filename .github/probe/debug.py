"""Temporary debug of preliminary visits for some parks (one at a time)."""
import html, http.cookiejar, re, sys, urllib.request
sys.path.insert(0, "scripts")
import fetch_history as fh
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.addheaders = [("User-Agent", "Mozilla/5.0")]
outer = op.open(fh.YTD_REPORT.format(code="YELL"), timeout=60).read().decode()
page = op.open(fh.IRMA + html.unescape(re.search(r'src="([^"]+)"', outer).group(1)), timeout=90).read().decode("utf-8", "ignore")
f = fh._ReportForm(); f.feed(page)
park = next(k for k, o in f.selects.items() if len(o) > 100)
labels = [t.replace("\xa0", " ").strip() for _, t in f.selects[park]]
print("park options matching:", [l for l in labels if re.search(r"carls|chiric|cavern|kings|sequoia|gateway|new river|white sands|indiana|hot springs", l, re.I)])
e = re.search(r'"ExportUrlBase":"([^"]*)"', page).group(1).replace("\\u0026", "&")
csv = op.open(fh.IRMA + e + "CSV", timeout=90).read().decode("utf-8-sig", "ignore")
print("YELL lines with total or recreation:")
print("\n".join(l for l in csv.splitlines() if re.search(r"total|recreation", l, re.I)))
