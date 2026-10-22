#!/usr/bin/env python3
"""Download REAL fruit photographs from Wikimedia Commons (free licenses).

Resolves each File: title through the Commons API to a direct thumb URL and
saves it into scripts/photos/<slug>.jpg.  Run once, then execute
scripts/make-photo-fruits.py to cut out the background and render the
24-frame 360 turntable used by the slider.
"""
import json, os, sys, time, urllib.parse, urllib.request

OUT = "scripts/photos"
UA = {"User-Agent": "AgrumeaCloneDev/1.0 (educational website clone preview; contact dev@example.com)"}

# local file -> [Commons File: titles, best first]
WANT = {
    "papaya.jpg":   ["File:Papaya cut half.jpg",
                     "File:Half a papaya showing the seeds 2016.jpg"],
    "melon.jpg":    ["File:Canteloupe and cross section.jpg",
                     "File:Cucumis melo var. reticulatus (photo by Scott Bauer).jpg"],
    "cane.jpg":     ["File:Sugarcane harvesting in Batad.jpg",
                     "File:Sapajus flavius holding a sugarcane stalk.jpg"],
    "rambutan.jpg": ["File:Rambutan white background alt.jpg",
                     "File:Rambutans with seed.jpg",
                     "File:Rambutan fruit, half peeled.jpg"],
    "dragon.jpg":   ["File:Webysther 20150409032418 - Pitaya.jpg",
                     "File:Hylocereus undatus-fruit20180201 118(07,24,36).jpg"],
}


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def thumb_url(title, width=1600):
    data = api({"action": "query", "titles": title, "prop": "imageinfo",
                "iiprop": "url|size", "iiurlwidth": str(width), "format": "json"})
    for p in data.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo")
        if ii:
            return ii[0].get("thumburl") or ii[0].get("url")
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    fails = []
    for fname, titles in WANT.items():
        dest = os.path.join(OUT, fname)
        done = False
        for title in titles:
            try:
                u = thumb_url(title)
                if not u:
                    print("no-api", fname, title); continue
                # strip utm params (some CDN proxies choke on them)
                base = u.split("?")[0]
                req = urllib.request.Request(base, headers=UA)
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = r.read()
                if len(data) < 30000:
                    print("small", fname, len(data)); continue
                with open(dest, "wb") as f:
                    f.write(data)
                print("OK", fname, len(data), "<-", title)
                done = True; break
            except Exception as e:
                print("retry", fname, title, str(e)[:80]); time.sleep(2)
        if not done:
            fails.append(fname)
    if fails:
        print("FAILED:", fails); sys.exit(1)


if __name__ == "__main__":
    main()
