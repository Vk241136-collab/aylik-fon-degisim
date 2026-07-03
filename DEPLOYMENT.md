# aylıkfondeğişim.com Yayınlama Planı

Bu proje üç parçadan oluşur:

1. Next.js web sitesi
2. FastAPI backend
3. KAP veri toplama worker'ı

## Domain

Görünen alan adı:

```text
aylıkfondeğişim.com
```

DNS ve bazı hosting panellerinde kullanılacak teknik IDN karşılığı:

```text
xn--aylkfondeiim-lyb9vxz.com
```

Önerilen DNS kayıtları:

- `aylıkfondeğişim.com` -> Vercel frontend
- `www.aylıkfondeğişim.com` -> Vercel frontend
- `api.aylıkfondeğişim.com` -> FastAPI backend

## Önerilen İlk Canlı Kurulum

- Frontend: Vercel
- Backend: Render veya Railway
- Veritabanı: Render PostgreSQL, Railway PostgreSQL, Neon veya Supabase
- Dosya saklama: İlk aşamada backend disk alanı, üretimde Cloudflare R2 veya S3
- Worker: Backend platformunda ayrı worker servisi

## Vercel Frontend

1. GitHub reposunu Vercel'e bağla.
2. Root directory olarak `frontend` seç.
3. Environment variable ekle:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.xn--aylkfondeiim-lyb9vxz.com/api
```

4. Domain olarak `aylıkfondeğişim.com` ve `www.aylıkfondeğişim.com` ekle.

## Render Backend

`render.yaml` dosyası backend API, worker ve PostgreSQL için hazırlandı.

Canlıya almadan önce:

```text
KAP_SYNC_ENABLED=false
```

olarak kalmalı. KAP erişim yöntemi ve kullanım koşulları netleşince:

```text
KAP_SYNC_ENABLED=true
```

yapılır.

## KAP Veri Hattı

Canlı mimari:

```text
KAP kontrol worker'ı
  -> fon katalog senkronizasyonu
  -> fon bildirimleri tarama
  -> rapor eki indirme
  -> PDF/Excel parser
  -> veri kalite kontrolü
  -> karşılaştırma üretimi
  -> web dashboard
```

KAP için tercih sırası:

1. Resmi veya sözleşmeli veri servisi
2. KAP'ın izin verdiği indirilebilir dosya/endpoint
3. Düşük frekanslı, cache'li ve robots/kullanım şartlarına uygun sayfa izleme

Agresif scraping yapılmamalı. Veri hattı `KAP_SYNC_ENABLED=false` ile güvenli başlangıç modunda gelir.

## İlk Yayın Kontrol Listesi

- Domain satın alındı mı?
- GitHub reposu hazır mı?
- Vercel hesabı bağlandı mı?
- Backend platformu seçildi mi?
- PostgreSQL oluşturuldu mu?
- `DATABASE_URL` tanımlandı mı?
- `NEXT_PUBLIC_API_BASE_URL` canlı API adresini gösteriyor mu?
- `CORS_ORIGINS` canlı domainleri içeriyor mu?
- KAP veri erişim yöntemi netleşti mi?
- KVKK/gizlilik, kullanım koşulları ve yatırım tavsiyesi değildir uyarısı eklendi mi?
