#!/usr/bin/env python3
"""Eklenti .cs3 dosyalarından domain çıkarır ve erişilebilirliği ölçer."""
import json
import re
import urllib.request
import zipfile
import io
import concurrent.futures

HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
SKIP = re.compile(r"(github|githubusercontent|jsdelivr|cloudflare|google|gstatic|"
                  r"schema\.org|w3\.org|json-schema|kotlinlang|apache\.org|okhttp|"
                  r"openh264|exoplayer|androidx|tmdb|imdb|sentry|googlesyndication)", re.I)


def get(url, t=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=t)


def domains_from(cs3_url):
    try:
        raw = get(cs3_url).read()
        z = zipfile.ZipFile(io.BytesIO(raw))
        blob = b"".join(z.read(n) for n in z.namelist() if n.endswith(".dex"))
        txt = blob.decode("utf-8", "ignore")
        found = set(re.findall(r"https?://([a-z0-9.-]+\.[a-z]{2,})", txt, re.I))
        return {d.lower() for d in found if not SKIP.search(d)}
    except Exception as e:
        return set()


def reachable(dom):
    for scheme in ("https", "http"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                f"{scheme}://{dom}/", headers=HDR), timeout=12)
            return r.status
        except Exception as e:
            code = getattr(e, "code", None)
            if code:
                return code
    return 0


def main():
    pl = json.load(open("/home/soner/Belgeler/lilit-cs/plugins.json"))
    # sadece spor + canlı yayın eklentileri
    want = [p for p in pl if any(k in (p.get("name") or "").lower() for k in
            ("spor", "tv", "sports", "stream", "yayin", "taraftar", "selcuk", "canli", "golge"))]
    print(f"{len(want)} eklenti inceleniyor\n")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        doms = dict(zip([p["name"] for p in want],
                        ex.map(lambda p: domains_from(p["url"]), want)))
    all_doms = sorted({d for s in doms.values() for d in s})
    print(f"{len(all_doms)} farklı domain\n")
    with concurrent.futures.ThreadPoolExecutor(20) as ex:
        codes = dict(zip(all_doms, ex.map(reachable, all_doms)))
    for name, ds in doms.items():
        alive = [d for d in ds if codes.get(d) in (200, 301, 302, 403, 401)]
        dead = [d for d in ds if codes.get(d) == 0]
        status = "VPN'siz açık" if alive and not dead else ("kısmen" if alive else "KAPALI")
        print(f"{name}: {status} | açık={len(alive)} kapalı={len(dead)}")
        for d in sorted(dead)[:6]:
            print(f"    ✗ {d}")


if __name__ == "__main__":
    main()
