"""Temporary probe 4: CORS of the ArcGIS web map data, and sample NPS Park Tiles (base64)."""
import base64, json, urllib.request
H = {"User-Agent": "Mozilla/5.0", "Origin": "https://minhlong94.github.io", "Referer": "https://minhlong94.github.io/"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as r:
        return r.status, dict(r.headers), r.read()
ids = {"standard": "d22a7a13a81045b4a90574fe934162f5", "slate": "0ae162fa27464b3183316205165d93ae", "light": "1da9245ce41f46109b00dac4c87959c5"}
for name, i in ids.items():
    st, h, b = get(f"https://www.arcgis.com/sharing/rest/content/items/{i}/data?f=json")
    print(name, "data", st, "ACAO=", h.get("Access-Control-Allow-Origin"), "cache=", h.get("Cache-Control"))
    tpl = json.loads(b)["baseMap"]["baseMapLayers"][0]["templateUrl"]
    # Yellowstone area, z=10: x=196..197 y=372..373 ; one tile
    for z, x, y in [(10, 196, 372), (12, 786, 1490)]:
        u = tpl.replace("{level}", str(z)).replace("{col}", str(x)).replace("{row}", str(y)).replace("@2x", "")
        try:
            st, h, b = get(u)
            print(name, "TILE", z, x, y, st, h.get("Content-Type"), len(b), "ACAO=", h.get("Access-Control-Allow-Origin"), "cache=", h.get("Cache-Control"))
            print("B64", name, z, base64.b64encode(b).decode())
        except Exception as e:
            print(name, "TILE ERR", e)
# no referer
try:
    req = urllib.request.Request(tpl.replace("{level}", "10").replace("{col}", "196").replace("{row}", "372"), headers={"User-Agent": "x"})
    print("no-referer", urllib.request.urlopen(req, timeout=30).status)
except Exception as e:
    print("no-referer ERR", e)
