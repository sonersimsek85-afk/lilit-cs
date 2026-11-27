#!/usr/bin/env python3
"""Film/dizi sağlayıcıları için örnek arama ("avatar") testi."""
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
PATHS = [
    "/?s={q}", "/search?q={q}", "/arama?query={q}", "/arama?q={q}",
    "/search/{q}", "/ara?q={q}",
]
HELPER = (
    "inv.nadeko.net", "kreosus.com", "strawpoll.com", "ok.ru",
    "odnoklassniki.ru", "my.mail.ru", "api.themoviedb.org",
    "pixeldrain.com", "2cms.cc",
)


def fetch(url, timeout=9):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:
        return type(e).__name__, "", b""


def test_one(args):
    name, domain, path = args
    url = "https://" + domain + path.format(q=urllib.parse.quote("avatar"))
    st, final, body = fetch(url)
    text = body.decode("utf-8", "ignore")
    hits = len(re.findall(r"avatar", text, re.I))
    resulty = bool(re.search(r"<a\s[^>]*href=", text, re.I)) and hits >= 2
    return {"name": name, "domain": domain, "path": path, "code": st,
            "final": final, "hits": hits, "resulty": resulty, "bytes": len(body)}


def main():
    plugins = json.load(open("plugins.json", encoding="utf-8"))
    sites = json.load(open("site-test.json", encoding="utf-8"))
    live = {"Live"}
    jobs = []
    for p, s in zip(plugins, sites):
        types = set(p.get("tvTypes", []))
        if types and types <= live:
            continue
        for d in s["ok"]:
            if any(h in d for h in HELPER):
                continue
            for path in PATHS:
                jobs.append((p["name"], d, path))
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        rows = list(ex.map(test_one, jobs))
    by_name = {}
    for r in rows:
        by_name.setdefault(r["name"], []).append(r)
    out = []
    for p, s in zip(plugins, sites):
        types = set(p.get("tvTypes", []))
        if types and types <= live:
            out.append({"name": p["name"], "tur": "LIVE", "arama": None, "bulundu": None})
            continue
        tests = by_name.get(p["name"], [])
        good = [r for r in tests if r["code"] == 200 and r["resulty"]]
        out.append({"name": p["name"], "tur": "FILM/DIZI",
                    "arama": good[0] if good else None,
                    "bulundu": bool(good),
                    "denenen": len(tests)})
    json.dump(out, open("search-test.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    film = [r for r in out if r["tur"] == "FILM/DIZI"]
    print("YAZILDI search-test.json | film/dizi", len(film),
          "| arama sonucu alan", sum(bool(r["bulundu"]) for r in film))


if __name__ == "__main__":
    main()
