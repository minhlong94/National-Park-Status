"""Temporary probe: public NPS map tile services (R71)."""
import json, re, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (National-Park-Status probe)"}
def get(u, raw=False):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
            b = r.read().decode("utf-8", "ignore")
            return b if raw else json.loads(b)
    except Exception as e:
        return f"ERROR {e}"
ORG = "fBc8EJBxQRMcHlei"
for q in [f'orgid:{ORG} AND (type:"Map Service" OR type:"Vector Tile Service") AND (tiles OR basemap OR "park tiles")',
          '"park tiles" AND (type:"Map Service" OR type:"Vector Tile Service" OR type:"Web Map")',
          f'orgid:{ORG} AND title:"Park Tiles"']:
    j = get("https://www.arcgis.com/sharing/rest/search?f=json&num=40&q=" + urllib.parse.quote(q))
    print("== search:", q)
    if isinstance(j, str): print(j); continue
    for it in j.get("results", []):
        print("  -", it.get("title"), "|", it.get("type"), "|", it.get("access"), "|", it.get("url"), "|", it.get("owner"), "|", (it.get("licenseInfo") or "")[:120].replace("\n", " "))
for u in [f"https://tiles.arcgis.com/tiles/{ORG}/arcgis/rest/services?f=json", f"https://vectortileservices1.arcgis.com/{ORG}/arcgis/rest/services?f=json",
          f"https://services1.arcgis.com/{ORG}/arcgis/rest/services?f=json"]:
    j = get(u); print("==", u)
    if isinstance(j, str): print(j[:300]); continue
    names = [s.get("name") + " (" + s.get("type", "") + ")" for s in j.get("services", [])]
    print("  ", len(names), [n for n in names if re.search(r"tile|basemap|park_?tiles|base", n, re.I)][:40])
for u in ["https://www.nps.gov/maps/tools/park-tiles/", "https://www.nps.gov/maps/tools/park-tiles/index.html"]:
    h = get(u, raw=True); print("==", u, len(h))
    for m in sorted(set(re.findall(r'https?://[^"\'\s<>]+', h))):
        if re.search(r"tile|mapbox|arcgis|style", m, re.I): print("   ", m[:200])
