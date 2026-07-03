# Aylık Fon Değişim

`aylıkfondeğişim.com`, Türkiye'deki yatırım fonlarının aylık portföy dağılım raporlarını izlemek, iki dönem arasındaki varlık değişimlerini hesaplamak ve yatırımcıya anlaşılır grafiklerle sunmak için geliştirilen web uygulamasıdır.

Teknik domain karşılığı:

```text
xn--aylkfondeiim-lyb9vxz.com
```

## Ürün Hedefi

- Türkiye'deki farklı fon türlerini tek katalogda göstermek
- Fon bilgilerini ve fon bildirimlerini KAP kaynaklı veri hattından güncellemek
- Aylık portföy raporlarını PDF, Excel veya CSV formatından ayrıştırmak
- Fonun iki dönem arasındaki tüm varlık değişimlerini hesaplamak
- Yeni giren, çıkan, ağırlığı artan/azalan ve manuel kontrol gerektiren pozisyonları göstermek
- Hisse senedi özel analizi, varlık sınıfı dağılımı, yoğunlaşma ve döviz dağılımı grafiklerini üretmek

## Mevcut Kapsam

- Next.js tabanlı web sitesi
- Fon kataloğu ve fon seçme arayüzü
- FastAPI backend
- PostgreSQL için SQLAlchemy modelleri
- PDF, XLSX, XLS ve CSV parser altyapısı
- Esnek kolon eşleme
- Türkçe sayı/yüzde normalizasyonu
- `Decimal` tabanlı finansal hesaplama motoru
- RapidFuzz destekli varlık eşleştirme
- KAP senkronizasyon servis iskeleti
- Ayrı KAP worker süreci
- Docker Compose yerel geliştirme düzeni
- Vercel frontend ve Render backend yayınlama dosyaları

## Yerelde Çalıştırma

```bash
docker compose up --build
```

Adresler:

- Web sitesi: `http://localhost:3000`
- API: `http://localhost:8000`
- API dokümanı: `http://localhost:8000/docs`

İlk açılışta 10 örnek fon ve her biri için Mayıs 2026 / Haziran 2026 örnek portföy verisi gelir.

## KAP Veri Hattı

KAP senkronizasyonu güvenli başlangıç modunda kapalı gelir:

```text
KAP_SYNC_ENABLED=false
```

KAP erişim yöntemi ve kullanım koşulları netleşince:

```text
KAP_SYNC_ENABLED=true
```

KAP worker akışı:

```text
KAP kontrolü
  -> fon kataloğu senkronizasyonu
  -> fon bildirimleri tarama
  -> rapor eki indirme
  -> parser kuyruğu
  -> veri kalite kontrolü
  -> karşılaştırma üretimi
  -> dashboard
```

KAP durum endpointleri:

- `GET /api/kap/status`
- `POST /api/kap/sync`

## Fon Kataloğu CSV İçe Aktarma

Türkiye'deki tüm fonları başlangıçta CSV ile içeri almak için:

```bash
curl -F "file=@fon_katalogu.csv" http://localhost:8000/api/funds/import-catalog
```

CSV kolonları:

- Fon kodu: `code`, `Fon Kodu`, `fon_kodu`
- Fon adı: `name`, `Fon Adı`, `fon_adi`
- Portföy şirketi: `company`, `Kurucu`, `portfoy_yonetim_sirketi`

## Yayınlama

Ayrıntılı canlıya alma rehberi:

```text
DEPLOYMENT.md
```

Önerilen ilk canlı mimari:

- Frontend: Vercel
- Backend API: Render veya Railway
- Worker: Render/Railway worker servisi
- Veritabanı: PostgreSQL
- Dosya saklama: Cloudflare R2, S3 veya MinIO
- Domain: `aylıkfondeğişim.com`
- API domain: `api.aylıkfondeğişim.com`

## Test

```bash
cd backend
python -m pytest
```

Testler yeni giren/çıkan pozisyonları, ağırlık/adet ayrışmasını, Türkçe ondalık formatını ve fuzzy eşleştirmeyi kapsar.

## Önemli Not

Bu uygulama yatırım tavsiyesi üretmez. Hesaplanan sonuçlar KAP bildirimlerinden ve yüklenen raporlardan türetilen analitik çıktılardır. Canlı yayında kullanım koşulları, gizlilik politikası ve “yatırım tavsiyesi değildir” uyarısı eklenmelidir.
