#!/usr/bin/env python3
"""Lilit CS repo — tek depo, tek liste.

Kaynak depoların eklenti listelerini birleştirir, isim çakışmalarını ayıklar ve
plugins.json üretir. repo.json bu listeye işaret eder; GitHub Actions günde bir kez
çalıştırır, böylece kaynak depolara eklenen yeni eklentiler otomatik gelir.
"""
import json
import urllib.request

SOURCES = [
    # (etiket, repo.json adresi, dahil edilecek isimler | None = hepsi)
    ("WioSpor", "https://raw.githubusercontent.com/Wiojelt/WioSpor/main/repo.json", None),
    ("WioSinema", "https://raw.githubusercontent.com/Wiojelt/WioSinema/main/repo.json", None),
    ("BTVault", "https://raw.githubusercontent.com/baristomruk-max/BTVault/main/repo.json",
     {"SporTV", "GolgeTV", "vavooSpor", "CanliTV"}),  # sadece spor/canlı, +18 hariç
    ("LilitKoleksiyon", "https://raw.githubusercontent.com/sonersimsek85-afk/lilit-koleksiyon/main/repo.json", None),
]

OUT = "plugins.json"

# LilitKoleksiyon tek .cs3 içinde bu siteleri zaten taşıyor.
# Diğer kaynaklardaki aynı site kopyalarını atla; aksi hâlde TV'de çift görünür.
KOLEKSIYON_ICINDEKILER = {
    "hdfilmcehennemi",
    "fullhdfilmizlesene",
    "diziyou",
    "dizipal",
    "dizipalhub",
    "anizium",
}

# Site erişim taramasında gerçek site domaini hiç açılmayanlar
# (site-test.json, 26.11 ölçümü). iptv-org tabanlı CanliTV/vavooSpor korunur.
OLU_SITELER = {
    "filmmakinesi",
    "fullhdfilm",
    "powersinema",
    "rectv",
    "tranimaci",
    "wfilmizle",
}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def load_plugins(repo_url):
    repo = fetch(repo_url)
    out = []
    for lst in repo.get("pluginLists", []):
        out.extend(fetch(lst))
    return out


def main():
    merged, seen_names, seen_urls = [], set(), set()
    stats = {}
    for label, url, allow in SOURCES:
        try:
            items = load_plugins(url)
        except Exception as exc:  # kaynak ölüyse diğerleri yine çalışsın
            print(f"UYARI {label}: {exc}")
            stats[label] = 0
            continue
        added = 0
        for it in items:
            name = it.get("name") or it.get("internalName")
            purl = it.get("url")
            if not name or not purl:
                continue
            if allow is not None and name not in allow:
                continue
            key = name.casefold()
            internal = (it.get("internalName") or "").casefold()
            if (key in KOLEKSIYON_ICINDEKILER
                    or internal in KOLEKSIYON_ICINDEKILER
                    or key in OLU_SITELER
                    or internal in OLU_SITELER):
                continue
            if key in seen_names or purl in seen_urls:
                continue
            seen_names.add(key)
            seen_urls.add(purl)
            merged.append(it)
            added += 1
        stats[label] = added
        print(f"{label}: {len(items)} kaynak -> {added} alındı")

    merged.sort(key=lambda x: (x.get("name") or "").casefold())
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=2)
    print(f"toplam {len(merged)} eklenti -> {OUT}")


if __name__ == "__main__":
    main()
