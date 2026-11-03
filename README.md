# Lilit — tek CloudStream deposu

Türkçe spor, canlı TV, film ve dizi eklentilerini tek depoda toplar.

## Depo adresi
```
https://raw.githubusercontent.com/sonersimsek85-afk/lilit-cs/main/repo.json
```

Kısa yol: `https://tinyurl.com/lilit`

## Nasıl eklenir
CloudStream → Ayarlar → Eklentiler → sağ alt buton → yukarıdaki adresi yapıştır → Depo ekle →
depo kartından **İndir** → uygulamayı yeniden başlat.

## İçerik
- `build.py` kaynak depoların eklenti listelerini birleştirir (WioSpor + WioSinema + BTVault'tan
  4 spor/canlı sağlayıcı), isim çakışmalarını ayıklar.
- `.github/workflows/sync.yml` her gün 03:17'de listeyi yeniler.
- +18 sağlayıcılar bilinçli olarak dahil edilmez.

## Not
Depo kurulumu yayınları engelleyen ISS filtrelerini aşmaz; bazı sağlayıcılar (Taraftarium24,
SelcukSports vb.) için VPN gerekir.
