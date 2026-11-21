"""Temporary probe: get one month of the IRMA "Park YTD Version 1" report with a form postback."""
import html, http.cookiejar, re, sys, urllib.parse, urllib.request
from html.parser import HTMLParser

BASE = "https://irma.nps.gov"
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.addheaders = [("User-Agent", "Mozilla/5.0")]

def get(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    with op.open(urllib.request.Request(url, data=body), timeout=90) as r:
        return r.geturl(), r.read().decode("utf-8", "ignore")

class Form(HTMLParser):
    def __init__(self):
        super().__init__(); self.fields = {}; self.selects = {}; self.cur = None; self.action = None
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "form" and self.action is None: self.action = a.get("action")
        if tag == "input" and a.get("name") and a.get("type", "text") in ("hidden", "text"):
            self.fields[a["name"]] = a.get("value", "")
        if tag == "select" and a.get("name"):
            self.cur = a["name"]; self.selects[self.cur] = {"disabled": "disabled" in a, "opts": [], "sel": None}
        if tag == "option" and self.cur:
            self.selects[self.cur]["opts"].append([a.get("value"), ""])
            if "selected" in a: self.selects[self.cur]["sel"] = a.get("value")
    def handle_data(self, d):
        if self.cur and self.selects[self.cur]["opts"]: self.selects[self.cur]["opts"][-1][1] += d
    def handle_endtag(self, tag):
        if tag == "select": self.cur = None

def parse(page):
    f = Form(); f.feed(page)
    for k, s in f.selects.items():
        print(f"  select {k}: disabled={s['disabled']} n={len(s['opts'])} sel={s['sel']} first={[o[1].replace(chr(160),' ') for o in s['opts'][:3]]}")
    return f

def post(url, f, changes):
    data = dict(f.fields)
    for k, s in f.selects.items():
        if not s["disabled"] and s["sel"] is not None: data[k] = s["sel"]
    data.update(changes)
    return get(url, data)

_, outer = get(BASE + "/Stats/SSRSReports/Park%20Specific%20Reports/Park%20YTD%20Version%201")
src = html.unescape(re.search(r'src="([^"]+)"', outer).group(1))
url, page = get(BASE + src)
print("viewer", url, len(page))
f = parse(page)
park_sel = next((k for k, s in f.selects.items() if any("Great Smoky" in o[1].replace(chr(160), " ") for o in s["opts"])), None)
mon_sel = next((k for k in f.selects if k != park_sel), None)
print("park select", park_sel, "month select", mon_sel)
grsm = next(o[0] for o in f.selects[park_sel]["opts"] if "Great Smoky" in o[1].replace(chr(160), " "))
post_url = urllib.parse.urljoin(url, html.unescape(f.action or url))
print("1) choose the park", grsm)
url2, page2 = post(post_url, f, {"__EVENTTARGET": park_sel, "__EVENTARGUMENT": "", park_sel: grsm})
print("  response", len(page2)); f2 = parse(page2)
months = f2.selects.get(mon_sel, {}).get("opts", [])
target = next((o[0] for o in months if o[1].replace(chr(160), " ").strip() == "Sep 2026"), None)
print("2) choose Sep 2026 =", target)
view_btn = next((k for k in f2.fields if k.endswith("$ctl00") and "ctl04" in k), "ReportViewer$ctl04$ctl00")
url3, page3 = post(post_url, f2, {park_sel: grsm, mon_sel: target, view_btn: "View Report", "__EVENTTARGET": "", "__EVENTARGUMENT": ""})
print("  response", len(page3)); parse(page3)
m = re.search(r'"ExportUrlBase":"([^"]*)"', page3)
if not m: print("no export url"); print(re.sub(r"\s+", " ", page3[:1500])); sys.exit(0)
exp = m.group(1).replace("\\u0026", "&")
_, csv = get(BASE + exp + "CSV")
print("CSV:"); print("\n".join(csv.splitlines()[:5]))
