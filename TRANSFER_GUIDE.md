# FFPAS - PC'ler Arası Transfer ve Kurulum Kılavuzu

## 📦 Adım 1: Mevcut PC'den Veriyi Dışa Aktar

### Linux / macOS

```bash
# Export scriptini çalıştırılabilir yap
chmod +x export_data.sh

# Export işlemini başlat
./export_data.sh
```

Bu script:
- Tüm uygulama dosyalarını toplar
- Veritabanını veya JSON dosyalarını kopyalar
- Model dosyalarını dahil eder
- Kurulum scriptlerini oluşturur
- Her şeyi tek bir `.tar.gz` arşivine sıkıştırır

**Çıktı:** `ffpas_export_YYYYMMDD_HHMMSS.tar.gz`

### Windows

```cmd
# Export scriptini çalıştır
export_data.bat
```

Bu script:
- Tüm uygulama dosyalarını toplar
- Veritabanını veya JSON dosyalarını kopyalar
- Model dosyalarını dahil eder
- Kurulum scriptlerini oluşturur
- Her şeyi tek bir `.zip` arşivine sıkıştırır

**Çıktı:** `ffpas_export_YYYYMMDD_HHMMSS.zip`

---

## 💾 Adım 2: Arşivi Yeni PC'ye Taşı

### Seçenek 1: USB Bellek
```bash
# USB'ye kopyala
cp ffpas_export_*.tar.gz /media/usb/

# Veya Windows'ta
copy ffpas_export_*.zip E:\
```

### Seçenek 2: Network Transfer (SCP)
```bash
# Linux/macOS
scp ffpas_export_*.tar.gz user@target-pc:/home/user/

# Windows (PowerShell)
scp ffpas_export_*.zip user@target-pc:/home/user/
```

### Seçenek 3: Cloud Storage
```bash
# Google Drive, Dropbox, OneDrive vb.
# Arşivi cloud'a yükle ve hedef PC'den indir
```

### Seçenek 4: Direkt Network Share
```bash
# Windows network share
\\server\share\ffpas_export_*.zip

# Linux Samba
smb://server/share/ffpas_export_*.tar.gz
```

---

## 🚀 Adım 3: Yeni PC'de Kurulum

### Otomatik Kurulum (Önerilen)

#### Linux / macOS

```bash
# 1. Arşivi çıkart
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. Quick setup scriptini çalıştır
chmod +x quick_setup.sh
./quick_setup.sh
```

Script otomatik olarak:
- ✅ Sistem gereksinimlerini kontrol eder
- ✅ Virtual environment oluşturur
- ✅ Bağımlılıkları yükler
- ✅ Dizinleri oluşturur
- ✅ .env dosyasını yapılandırır
- ✅ Veritabanını kontrol eder
- ✅ Testleri çalıştırır (opsiyonel)
- ✅ Sunucuyu başlatır (opsiyonel)

#### Windows

```cmd
# 1. ZIP dosyasını çıkart (sağ tık > Extract All)

# 2. Klasöre gir
cd ffpas_export_*

# 3. Quick setup scriptini çalıştır
quick_setup.bat
```

Script otomatik olarak:
- ✅ Sistem gereksinimlerini kontrol eder
- ✅ Virtual environment oluşturur
- ✅ Bağımlılıkları yükler
- ✅ Dizinleri oluşturur
- ✅ .env dosyasını yapılandırır
- ✅ Veritabanını kontrol eder
- ✅ Testleri çalıştırır (opsiyonel)
- ✅ Sunucuyu başlatır (opsiyonel)

---

### Manuel Kurulum

Eğer otomatik kurulum çalışmazsa:

#### 1. Arşivi Çıkart

```bash
# Linux/macOS
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# Windows
# ZIP dosyasına sağ tık > Extract All
cd ffpas_export_*
```

#### 2. Python Kurulumu

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

**Windows:**
- https://www.python.org/downloads/ adresinden Python 3.10+ indir
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretle

#### 3. Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 4. Bağımlılıkları Yükle

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Yapılandırma

```bash
# .env dosyasını oluştur
cp .env.example .env

# Düzenle
nano .env  # Linux/macOS
notepad .env  # Windows
```

#### 6. Dizinleri Oluştur

```bash
mkdir -p logs data
```

#### 7. Veritabanı

Eğer `data/matches.db` varsa, hazırsınız!

Eğer sadece JSON dosyaları varsa:
```bash
python database/migrate.py
```

#### 8. Sunucuyu Başlat

```bash
python start.py
```

---

## 🐳 Docker ile Kurulum (En Kolay)

Eğer Docker kuruluysa:

```bash
# 1. Arşivi çıkart
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. .env dosyasını yapılandır
cp .env.example .env
nano .env

# 3. Docker ile başlat
docker-compose up -d

# 4. Logları kontrol et
docker-compose logs -f

# 5. Durdur
docker-compose down
```

**Avantajları:**
- ✅ Python kurulumu gerekmez
- ✅ Bağımlılık sorunları olmaz
- ✅ Redis otomatik kurulur
- ✅ İzole ortam
- ✅ Kolay yönetim

---

## ✅ Kurulum Doğrulama

### 1. Health Check

```bash
curl http://localhost:5000/api/health
```

Beklenen çıktı:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "app": "FFPAS"
}
```

### 2. Detaylı Health Check

```bash
curl http://localhost:5000/api/health/detailed
```

### 3. API Dokümantasyonu

Tarayıcıda aç:
```
http://localhost:5000/api/docs
```

### 4. Test Prediction

```bash
curl -X POST "http://localhost:5000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Manchester United",
    "away_team": "Chelsea",
    "home_odds": 2.2,
    "draw_odds": 3.3,
    "away_odds": 3.1
  }'
```

### 5. Frontend

Tarayıcıda aç:
```
http://localhost:5000
```

---

## 🔧 Sorun Giderme

### Python Bulunamadı

**Linux:**
```bash
sudo apt install python3.10
```

**macOS:**
```bash
brew install python@3.10
```

**Windows:**
- Python'u PATH'e ekle
- Veya tam yol kullan: `C:\Python310\python.exe`

### Port Zaten Kullanımda

`.env` dosyasında portu değiştir:
```
PORT=5001
```

### Modül Bulunamadı

```bash
# Virtual environment'ı aktif et
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Bağımlılıkları yeniden yükle
pip install -r requirements.txt
```

### Veritabanı Hatası

```bash
# Veritabanını sıfırla
rm data/matches.db

# Migration'ı yeniden çalıştır
python database/migrate.py
```

### Redis Bağlantı Hatası

Redis opsiyoneldir. Kurulu değilse:

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Windows:**
- https://github.com/microsoftarchive/redis/releases
- Veya .env'de Redis'i devre dışı bırak

### İzin Hatası (Linux/macOS)

```bash
# Scriptlere çalıştırma izni ver
chmod +x *.sh

# Veya sudo ile çalıştır
sudo python start.py
```

---

## 📊 Veri Boyutları

Tipik arşiv boyutları:

| İçerik | Boyut |
|--------|-------|
| Sadece kod | ~5 MB |
| Kod + JSON veriler | ~200 MB |
| Kod + SQLite DB | ~100 MB |
| Kod + DB + Model | ~150 MB |
| Tam paket | ~200-300 MB |

---

## 🔄 Güncelleme Senaryoları

### Senaryo 1: Sadece Kod Güncellemesi

```bash
# Eski PC'de
./export_data.sh

# Yeni PC'de
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*
./quick_setup.sh
```

### Senaryo 2: Veri + Kod Güncellemesi

Export scripti otomatik olarak hem kodu hem veriyi dahil eder.

### Senaryo 3: Sadece Veritabanı Transferi

```bash
# Eski PC'de
scp data/matches.db user@new-pc:/path/to/ffpas/data/

# Yeni PC'de
# Veritabanı otomatik olarak kullanılır
```

---

## 🎯 Hızlı Referans

### Tek Komut Kurulum

**Linux/macOS:**
```bash
tar -xzf ffpas_export_*.tar.gz && cd ffpas_export_* && chmod +x quick_setup.sh && ./quick_setup.sh
```

**Windows:**
```cmd
REM ZIP'i çıkart, sonra:
cd ffpas_export_* && quick_setup.bat
```

### Sunucu Komutları

```bash
# Başlat
python start.py

# Veya development mode
uvicorn api.main:app --reload

# Docker ile
docker-compose up -d

# Durdur
Ctrl+C  # veya
docker-compose down
```

### Yararlı Komutlar

```bash
# Logları görüntüle
tail -f logs/app.log

# Testleri çalıştır
pytest

# Veritabanı istatistikleri
curl http://localhost:5000/api/stats/database

# Health check
curl http://localhost:5000/api/health/detailed
```

---

## 📞 Destek

Sorun yaşarsanız:

1. **Logları kontrol edin:**
   ```bash
   tail -f logs/app.log
   ```

2. **Health check yapın:**
   ```bash
   curl http://localhost:5000/api/health/detailed
   ```

3. **Dokümantasyonu okuyun:**
   - `README_V2.md` - Ana dokümantasyon
   - `UPGRADE_GUIDE.md` - Upgrade rehberi
   - `ANALIZ_RAPORU.md` - Detaylı analiz

4. **Test edin:**
   ```bash
   pytest tests/ -v
   ```

---

## ✨ İpuçları

### Hızlı Transfer için

1. **Sadece veritabanını taşı** (JSON'lar yerine):
   - `data/matches.db` dosyası ~100 MB
   - JSON dosyaları ~200 MB
   - %50 daha hızlı transfer

2. **Model dosyasını ayrı taşı**:
   - `ai_model.pt` büyükse ayrı transfer et
   - Sistem model olmadan da çalışır (düşük doğrulukla)

3. **Sıkıştırma seviyesini ayarla**:
   ```bash
   # Daha iyi sıkıştırma (daha yavaş)
   tar -czf archive.tar.gz --best folder/
   
   # Daha hızlı (daha büyük)
   tar -czf archive.tar.gz --fast folder/
   ```

### Güvenlik

1. **API anahtarlarını paylaşma**:
   - `.env` dosyası arşive dahil değil
   - Yeni PC'de yeniden yapılandır

2. **Veritabanını şifrele** (opsiyonel):
   ```bash
   # Şifrele
   gpg -c data/matches.db
   
   # Şifreyi çöz
   gpg data/matches.db.gpg
   ```

---

**Başarılar! 🚀**

Herhangi bir sorun yaşarsanız, dokümantasyonu kontrol edin veya destek alın.
