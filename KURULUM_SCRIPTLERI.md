# FFPAS - Kurulum Scriptleri Kullanım Kılavuzu

## 📋 Mevcut Scriptler

### 1. Export Scriptleri (Veri Dışa Aktarma)

#### `export_data.sh` (Linux/macOS)
Tüm uygulama, veri ve yapılandırma dosyalarını tek bir arşive toplar.

**Kullanım:**
```bash
chmod +x export_data.sh
./export_data.sh
```

**Çıktı:** `ffpas_export_YYYYMMDD_HHMMSS.tar.gz`

#### `export_data.bat` (Windows)
Windows için aynı işlevi görür.

**Kullanım:**
```cmd
export_data.bat
```

**Çıktı:** `ffpas_export_YYYYMMDD_HHMMSS.zip`

**Ne İçerir:**
- ✅ Tüm uygulama kodu (ai/, api/, database/, utils/, tests/)
- ✅ Yapılandırma dosyaları (config.py, requirements.txt, .env.example)
- ✅ Veritabanı (matches.db) veya JSON dosyaları
- ✅ Model dosyaları (ai_model.pt, goals_model.pt)
- ✅ Frontend dosyaları
- ✅ Dokümantasyon
- ✅ Otomatik kurulum scriptleri (install.sh/bat)
- ✅ Docker yapılandırması

---

### 2. Quick Setup Scriptleri (Hızlı Kurulum)

#### `quick_setup.sh` (Linux/macOS)
Tek komutla tüm kurulumu yapar.

**Kullanım:**
```bash
chmod +x quick_setup.sh
./quick_setup.sh
```

#### `quick_setup.bat` (Windows)
Windows için hızlı kurulum.

**Kullanım:**
```cmd
quick_setup.bat
```

**Ne Yapar:**
1. ✅ Sistem gereksinimlerini kontrol eder (Python, pip, Redis)
2. ✅ Virtual environment oluşturur
3. ✅ Tüm bağımlılıkları yükler
4. ✅ Gerekli dizinleri oluşturur (logs/, data/)
5. ✅ .env dosyasını yapılandırır
6. ✅ Veritabanını kontrol eder
7. ✅ Migration gerekiyorsa çalıştırır (opsiyonel)
8. ✅ Testleri çalıştırır (opsiyonel)
9. ✅ Sunucuyu başlatır (opsiyonel)

**Özellikler:**
- 🎨 Renkli çıktı (Linux/macOS)
- ⚡ Otomatik hata tespiti
- 🔍 Detaylı durum raporları
- 💬 İnteraktif seçenekler
- 📊 Kurulum özeti

---

## 🚀 Kullanım Senaryoları

### Senaryo 1: Yeni PC'ye Tam Transfer

**Kaynak PC'de:**
```bash
# 1. Veriyi dışa aktar
./export_data.sh

# 2. Arşivi hedef PC'ye kopyala
scp ffpas_export_*.tar.gz user@target-pc:/home/user/
```

**Hedef PC'de:**
```bash
# 1. Arşivi çıkart
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. Hızlı kurulum
./quick_setup.sh

# 3. Sunucu otomatik başlar!
```

**Toplam Süre:** 5-10 dakika (migration dahil)

---

### Senaryo 2: Sadece Kod Güncellemesi

Eğer veritabanı zaten varsa ve sadece kodu güncellemek istiyorsanız:

```bash
# Kaynak PC'de
./export_data.sh

# Hedef PC'de
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*
./quick_setup.sh
# Migration'ı atla (veritabanı zaten var)
```

---

### Senaryo 3: Docker ile Kurulum

**Kaynak PC'de:**
```bash
./export_data.sh
```

**Hedef PC'de:**
```bash
# 1. Arşivi çıkart
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. .env yapılandır
cp .env.example .env
nano .env

# 3. Docker ile başlat
docker-compose up -d

# Hepsi bu kadar!
```

**Avantajlar:**
- ✅ Python kurulumu gerekmez
- ✅ Bağımlılık sorunları olmaz
- ✅ Redis otomatik gelir
- ✅ 2 dakikada hazır

---

### Senaryo 4: Manuel Kurulum

Eğer scriptler çalışmazsa, arşiv içindeki `install.sh` veya `install.bat` kullanın:

```bash
# Linux/macOS
./install.sh

# Windows
install.bat
```

Bu scriptler daha basit ve adım adım kurulum yapar.

---

## 📊 Script Karşılaştırması

| Özellik | export_data | quick_setup | install |
|---------|-------------|-------------|---------|
| **Amaç** | Veri dışa aktarma | Otomatik kurulum | Manuel kurulum |
| **Platform** | Linux/macOS/Win | Linux/macOS/Win | Linux/macOS/Win |
| **İnteraktif** | Hayır | Evet | Evet |
| **Hata Kontrolü** | Temel | Kapsamlı | Temel |
| **Migration** | - | Opsiyonel | Opsiyonel |
| **Test** | - | Opsiyonel | Hayır |
| **Sunucu Başlatma** | - | Opsiyonel | Hayır |

---

## 🎯 Hangi Scripti Kullanmalıyım?

### Export İçin

**Her zaman:** `export_data.sh` veya `export_data.bat`
- Tek script, tüm platformlar için

### Kurulum İçin

**Önerilen:** `quick_setup.sh` veya `quick_setup.bat`
- En kapsamlı
- Otomatik hata tespiti
- İnteraktif seçenekler

**Alternatif:** `install.sh` veya `install.bat` (arşiv içinde)
- Daha basit
- Daha az soru sorar
- Hızlı kurulum

**Docker:** `docker-compose up -d`
- En kolay
- En güvenilir
- Önerilen production için

---

## 🔧 Script Özellikleri

### Export Scriptleri

**Güvenlik:**
- ✅ .env dosyası dahil edilmez (güvenlik)
- ✅ __pycache__ ve geçici dosyalar hariç
- ✅ Sadece gerekli dosyalar

**Optimizasyon:**
- ✅ Veritabanı varsa JSON'lar atlanır
- ✅ Sıkıştırma ile %70 daha küçük
- ✅ Hızlı transfer

**Esneklik:**
- ✅ Eksik dosyalar için uyarı (hata vermez)
- ✅ Otomatik tarih damgası
- ✅ Boyut bilgisi

### Quick Setup Scriptleri

**Akıllı Kontroller:**
- ✅ Python versiyonu kontrolü
- ✅ pip varlık kontrolü
- ✅ Redis kontrolü (opsiyonel)
- ✅ Disk alanı kontrolü

**Kullanıcı Dostu:**
- ✅ Renkli çıktı (Linux/macOS)
- ✅ İlerleme göstergeleri
- ✅ Başarı/hata mesajları
- ✅ Yardımcı öneriler

**Hata Yönetimi:**
- ✅ Her adımda hata kontrolü
- ✅ Geri dönülebilir işlemler
- ✅ Detaylı hata mesajları
- ✅ Çözüm önerileri

---

## 💡 İpuçları

### Export İçin

1. **Düzenli yedekleme:**
   ```bash
   # Cron job ekle (her gün 2:00'de)
   0 2 * * * cd /path/to/ffpas && ./export_data.sh
   ```

2. **Sadece veritabanını yedekle:**
   ```bash
   # Daha hızlı, daha küçük
   tar -czf db_backup.tar.gz data/matches.db
   ```

3. **Cloud'a otomatik yükle:**
   ```bash
   ./export_data.sh
   rclone copy ffpas_export_*.tar.gz gdrive:backups/
   ```

### Setup İçin

1. **Sessiz kurulum:**
   ```bash
   # Tüm sorulara "yes" cevabı ver
   yes | ./quick_setup.sh
   ```

2. **Sadece kontrol et:**
   ```bash
   # Kurulum yapma, sadece kontrol et
   ./quick_setup.sh --check-only  # (özelleştirme gerekir)
   ```

3. **Log kaydet:**
   ```bash
   ./quick_setup.sh 2>&1 | tee setup.log
   ```

---

## 🐛 Sorun Giderme

### "Permission denied" hatası

```bash
chmod +x export_data.sh quick_setup.sh
```

### "Command not found" hatası

```bash
# Tam yol kullan
bash export_data.sh
bash quick_setup.sh
```

### Windows'ta "not recognized" hatası

```cmd
REM PowerShell kullan
powershell -ExecutionPolicy Bypass -File export_data.bat
```

### Script yarıda kesildi

```bash
# Temizlik yap
rm -rf ffpas_export_*

# Yeniden dene
./export_data.sh
```

---

## 📚 Ek Kaynaklar

- **Detaylı Transfer Kılavuzu:** `TRANSFER_GUIDE.md`
- **Ana Dokümantasyon:** `README_V2.md`
- **Upgrade Rehberi:** `UPGRADE_GUIDE.md`
- **Analiz Raporu:** `ANALIZ_RAPORU.md`

---

## ✅ Kontrol Listesi

### Export Öncesi
- [ ] Tüm değişiklikler kaydedildi
- [ ] Veritabanı güncel
- [ ] Model dosyaları mevcut
- [ ] Yeterli disk alanı var

### Export Sonrası
- [ ] Arşiv oluşturuldu
- [ ] Boyut makul (100-300 MB)
- [ ] Arşiv bozuk değil (test et)
- [ ] Yedek kopyası alındı

### Kurulum Öncesi
- [ ] Python 3.10+ kurulu
- [ ] Yeterli disk alanı (1GB+)
- [ ] İnternet bağlantısı var
- [ ] Arşiv hedef PC'de

### Kurulum Sonrası
- [ ] Health check başarılı
- [ ] API docs açılıyor
- [ ] Test prediction çalışıyor
- [ ] Frontend erişilebilir

---

## 🎉 Başarı!

Scriptler hazır! Şimdi:

1. **Export için:**
   ```bash
   ./export_data.sh
   ```

2. **Kurulum için:**
   ```bash
   ./quick_setup.sh
   ```

3. **Veya Docker:**
   ```bash
   docker-compose up -d
   ```

**Kolay gelsin! 🚀**
