# Lilit — tek CloudStream deposu

Türkçe spor, canlı TV, film ve dizi eklentilerini tek depoda toplar.

## Depo adresi
```
https://raw.githubusercontent.com/sonersimsek85-afk/lilit-cs/main/repo.json
```

Kısa kod (arkadaşlarına ver): **`!lilit`**

> CloudStream **4.9.0 ve üzeri** gerekir: `!` ile başlayan shortcode'lar py.md üzerinden çözülür
> (4.8.0'da bu özellik yoktur). Eski sürümlerde aşağıdaki tam URL'yi kullanın.

Yedek adresler:
```
https://py.md/lilit
https://cdn.jsdelivr.net/gh/sonersimsek85-afk/lilit-cs@main/repo.json
```

## Nasıl eklenir
**Tek kelime (4.9.0+):** CloudStream → Ayarlar → Eklentiler → Depo ekle → "Depo URL'si veya kısa kod" alanına **`!lilit`** yaz → Depo ekle → depo kartından **İndir** → uygulamayı yeniden başlat.

**Eski sürüm / yedek:** aynı yerde yukarıdaki tam adreslerden birini yapıştır.

## İçerik
- `build.py` kaynak depoların eklenti listelerini birleştirir (WioSpor + WioSinema + BTVault'tan
  4 spor/canlı sağlayıcı), isim çakışmalarını ayıklar; LilitKoleksiyon içindeki siteleri, erişimi
  olmayan ve örnek aramada boş dönen eklentileri hariç tutar (şu an **59** eklenti).
- `.github/workflows/sync.yml` her gün 03:17 UTC'de listeyi yeniler.
- +18 sağlayıcılar bilinçli olarak dahil edilmez.

## Not
Depo kurulumu yayınları engelleyen ISS filtrelerini aşmaz; bazı sağlayıcılar (Taraftarium24,
SelcukSports vb.) için VPN gerekir.
