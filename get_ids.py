#!/usr/bin/env python3
"""
Q-SYS Reflect — Fetch Site ID, Core ID, System ID
Double-click this file to run. Results saved to results.txt
"""

import urllib.request
import urllib.error
import json
import os

API_KEY  = "d3f4d5bff1e0c6be40a7f05530ab68dd89591be66ca5e92b8fa48ab656941482"
BASE_URL = "https://reflect.qsc.com/api/public/v0"

ENDPOINTS = ["/cores", "/sites", "/systems", "/organizations"]

def fetch(path):
    url = BASE_URL + path
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body
    except Exception as e:
        return 0, {"error": str(e)}

def extract_ids(items):
    rows = []
    if not isinstance(items, list):
        items = [items]
    for item in items:
        rows.append({
            "name":      item.get("name") or item.get("displayName") or item.get("hostname") or "(unnamed)",
            "coreId":    item.get("coreId")   or item.get("id")        or "",
            "siteId":    item.get("siteId")   or item.get("site_id")   or "",
            "systemId":  item.get("systemId") or item.get("system_id") or "",
        })
    return rows

def print_table(rows, title):
    if not rows:
        return
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    for r in rows:
        print(f"  Name     : {r['name']}")
        if r['coreId']:   print(f"  Core ID  : {r['coreId']}")
        if r['siteId']:   print(f"  Site ID  : {r['siteId']}")
        if r['systemId']: print(f"  System ID: {r['systemId']}")
        print(f"  {'-'*50}")

def main():
    print("\nQ-SYS Reflect — ID Lookup")
    print("Connecting to reflect.qsc.com ...\n")

    all_rows = []

    for path in ENDPOINTS:
        print(f"  Trying {path} ...", end=" ", flush=True)
        status, data = fetch(path)

        if status == 0:
            print(f"Connection failed: {data.get('error','')}")
            continue
        elif status == 401:
            print("401 Unauthorized — check your API key")
            continue
        elif status == 403:
            print("403 Forbidden — no access to this endpoint")
            continue
        elif status == 404:
            print("404 Not found — skipping")
            continue
        elif status != 200:
            print(f"HTTP {status} — skipping")
            continue

        print(f"OK ({status})")

        items = data if isinstance(data, list) else \
                data.get("data") or data.get("cores") or \
                data.get("sites") or data.get("systems") or \
                data.get("items") or [data]

        rows = extract_ids(items)
        if rows:
            print_table(rows, path)
            all_rows.extend(rows)

    # Save to file
    if all_rows:
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.txt")
        with open(out_path, "w") as f:
            for r in all_rows:
                f.write(f"Name     : {r['name']}\n")
                f.write(f"Core ID  : {r['coreId']}\n")
                f.write(f"Site ID  : {r['siteId']}\n")
                f.write(f"System ID: {r['systemId']}\n")
                f.write("-" * 40 + "\n")
        print(f"\n  Results saved to: {out_path}")
    else:
        print("\n  No data returned. Please check your API key.")

    print("\nPress Enter to close...")
    input()

if __name__ == "__main__":
    main()
