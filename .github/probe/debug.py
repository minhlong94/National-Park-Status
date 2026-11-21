"""Temporary debug of preliminary visits for some parks (one at a time)."""
import sys
sys.path.insert(0, "scripts")
import fetch_history as fh
names = {p["code"].upper(): p["name"] for p in fh.load_parks()}
for code in ["ACAD", "CAVE", "CHIR", "YELL"]:
    print("==", code, names.get(code))
    try:
        print("  result:", fh.fetch_prelim_visits(code, ["2026-09"], name=names.get(code), debug=True))
    except Exception as e:
        print("  error:", e)
