"""Temporary probe 2: the layers of the NPS Park Tiles web maps, and a test tile without a key."""
import json, re, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (National-Park-Status probe)", "Referer": "https://minhlong94.github.io/"}
def get(u, raw=False):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
            b = r.read()
            return (r.status, r.headers.get("Content-Type"), b) if raw else json.loads(b.decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return (e.code, e.headers.get("Content-Type"), e.read()[:300]) if raw else f"ERROR {e.code} {e.read()[:200]}"
    except Exception as e:
        return (0, "", str(e).encode()) if raw else f"ERROR {e}"
q = 'owner:NPS_EGIS_AGOL AND title:"Park Tiles"'
j = get("https://www.arcgis.com/sharing/rest/search?f=json&num=20&q=" + urllib.parse.quote(q))
seen = set()
for it in j.get("results", []):
    print("==", it["title"], it["id"], it["type"])
    d = get(f"https://www.arcgis.com/sharing/rest/content/items/{it['id']}/data?f=json")
    if isinstance(d, str): print("  ", d); continue
    layers = (d.get("baseMap") or {}).get("baseMapLayers", []) + d.get("operationalLayers", [])
    for L in layers:
        url = L.get("url") or L.get("styleUrl") or ""
        print("   layer:", L.get("layerType"), L.get("title"), url, L.get("itemId"), L.get("templateUrl", ""))
        for cand in [u for u in [L.get("url"), L.get("styleUrl"), L.get("templateUrl")] if u]:
            if cand in seen: continue
            seen.add(cand)
            if "{" in cand:  # template: fill a tile near Yellowstone, z=8
                t = cand.replace("{level}", "8").replace("{z}", "8").replace("{col}", "50").replace("{x}", "50").replace("{row}", "93").replace("{y}", "93").replace("{subDomain}", "a").replace("{s}", "a")
                st, ct, b = get(t, raw=True); print("     tile", st, ct, len(b), t[:150])
            elif "VectorTileServer" in cand or "MapServer" in cand:
                info = get(cand + ("&" if "?" in cand else "?") + "f=json")
                print("     info:", (json.dumps(info)[:300] if not isinstance(info, str) else info))
                tile = cand.rstrip("/") + ("/tile/8/93/50.pbf" if "VectorTileServer" in cand else "/tile/8/93/50")
                st, ct, b = get(tile, raw=True); print("     tile", st, ct, len(b), tile[:150])
            elif cand.endswith(".json") or "style" in cand.lower():
                sty = get(cand)
                print("     style:", json.dumps(sty)[:400] if not isinstance(sty, str) else sty)
                if isinstance(sty, dict):
                    for name, src in (sty.get("sources") or {}).items():
                        print("       source", name, src.get("type"), src.get("url"), (src.get("tiles") or [""])[0][:150])
