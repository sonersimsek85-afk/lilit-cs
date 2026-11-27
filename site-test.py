#!/usr/bin/env python3
"""Lilit paketindeki her eklentinin site domainlerini ölçer."""
import concurrent.futures
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
SKIP = (
    "google", "gstatic", "github", "android", "localhost", "127.0.0.1",
    "cloudflare", "jsdelivr", "w3.org", "schema.org", "invidious",
    "example", "doubleclick", "googleapis", "gvideo", "ytimg", "youtu",
    "facebook", "twitter", "telegram", "t.me", "apple", "microsoft",
    "amazonaws", "cloudfront", "akamaized", "fastly", "playwright",
    "inv.nadeko.net", "kreosus.com", "strawpoll.com", "ok.ru",
    "odnoklassniki.ru", "my.mail.ru", "strem.io", "baby-beamup.club",
    "pixeldrain.com", "themoviedb.org", "thetvdb.com", "imdb.com",
)


def get(url, timeout=18):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.read()


def domains_for_plugin(p, limit=25):
    url = p.get("url", "")
    try:
        st, _, body = get(url, timeout=25)
        if st != 200:
            return [], f"indirme {st}"
        z = zipfile.ZipFile(io.BytesIO(body))
        text = ""
        for n in z.namelist():
            if n.endswith((".dex", ".json", ".txt")):
                try:
                    text += z.read(n).decode("latin-1", "ignore")
                except Exception:
                    pass
        found = []
        for d in re.findall(r"https?://([A-Za-z0-9._-]+)", text):
            d = d.lower().strip(".")
            if "." not in d or d == "x.com" or any(s in d for s in SKIP):
                continue
            if d not in found:
                found.append(d)
            if len(found) >= limit:
                break
        return found, ""
    except Exception as e:
        return [], type(e).__name__


def test_domain(d):
    try:
        st, final, body = get("https://" + d, timeout=10)
        sample = body[:400].decode("utf-8", "ignore").lower()
        return {"domain": d, "code": st, "final": final,
                "html": ("<html" in sample or "<!doctype" in sample),
                "bytes": len(body)}
    except urllib.error.HTTPError as e:
        return {"domain": d, "code": e.code, "final": "", "html": False, "bytes": 0}
    except Exception as e:
        return {"domain": d, "code": type(e).__name__, "final": "", "html": False, "bytes": 0}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "plugins.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "site-test.json"
    plugins = json.load(open(path, encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(10) as ex:
        doms = list(ex.map(domains_for_plugin, plugins))
    jobs = []
    for i, (p, (ds, err)) in enumerate(zip(plugins, doms)):
        for d in ds:
            jobs.append((i, d))
    with concurrent.futures.ThreadPoolExecutor(14) as ex:
        results = list(ex.map(lambda j: (j[0], test_domain(j[1])), jobs))
    by_i = {}
    for i, r in results:
        by_i.setdefault(i, []).append(r)
    rows = []
    for i, p in enumerate(plugins):
        ds, err = doms[i]
        tests = by_i.get(i, [])
        ok = [r for r in tests if r["code"] == 200 and r["html"]]
        rows.append({"name": p.get("name"), "internalName": p.get("internalName"),
                     "url": p.get("url"), "domains": ds, "tests": tests,
                     "ok": [r["domain"] for r in ok], "fetch_error": err})
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("YAZILDI", out, "| eklenti", len(rows),
          "| en az bir açık site", sum(bool(r["ok"]) for r in rows))


if __name__ == "__main__":
    main()
