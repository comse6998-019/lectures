#!/usr/bin/env python3
"""Ground lecture-7 literature on OpenAlex: venue, year, citation count.

Usage:
  litsearch.py search "query string"       # top matches for a query
  litsearch.py batch queries.txt           # one query per line, best match each
"""
import json
import sys
import time
import urllib.parse
import urllib.request

OA = "https://api.openalex.org/works"
MAILTO = "comse6998@example.com"


def fetch(query, per_page=4):
    enc = urllib.parse.quote(query)
    url = f"{OA}?search={enc}&per_page={per_page}&mailto={MAILTO}"
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=25) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if attempt == 4:
                return {"_error": str(e), "results": []}
            time.sleep(2 * (attempt + 1))
    return {"results": []}


def venue_of(w):
    pl = w.get("primary_location") or {}
    src = pl.get("source") or {}
    return src.get("display_name") or ""


def row(w):
    ids = w.get("ids", {}) or {}
    doi = (ids.get("doi") or "").replace("https://doi.org/", "")
    year = w.get("publication_year")
    cites = w.get("cited_by_count")
    venue = venue_of(w)[:38]
    title = (w.get("title") or "")[:72]
    return f"  {str(year):>4} | cites={str(cites):>6} | {venue:38} | {title} | doi:{doi}"


def search(query):
    d = fetch(query)
    if d.get("_error"):
        print(f"  ERROR: {d['_error']}")
        return
    for w in d.get("results", []):
        print(row(w))


def batch(path):
    with open(path) as f:
        queries = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    for q in queries:
        print(f"### {q}")
        d = fetch(q, per_page=1)
        results = d.get("results", [])
        if not results:
            print("  (no result)")
        else:
            print(row(results[0]))
        time.sleep(0.4)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "search":
        search(arg)
    elif cmd == "batch":
        batch(arg)
    else:
        print(__doc__)
        sys.exit(1)
