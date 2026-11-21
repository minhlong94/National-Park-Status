"""Temporary debug: Redwood report rows for Jan and May 2026."""
import sys
sys.path.insert(0, "scripts")
import fetch_history as fh
print(fh.fetch_prelim_visits("REDW", ["2026-01", "2026-05"], "Redwood", debug=True, prev={"2026-01": 48394, "2026-05": 119782}))
