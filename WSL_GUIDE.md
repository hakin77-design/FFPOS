# FFPAS v2.0 - WSL Ubuntu Kurulum ve Transfer Kılavuzu

## 🐧 WSL Ubuntu için Özel Kılavuz

Bu kılavuz, FFPAS'ı WSL (Windows Subsystem for Linux) Ubuntu ortamında çalıştırmak ve başka bir PC'ye transfer etmek için hazırlanmıştır.

---

## 📦 Mevcut PC'den Export (WSL Ubuntu)

### Hızlı Export

```bash
# Export scriptini çalıştırılabilir yap
chmod +x wsl_export.sh

# Export işlemini başlat
./wsl_export.sh
```

**Bu script:**
- ✅ Tüm dosyaları toplar
- ✅ Arşiv oluşturur
- ✅ Windows Desktop'a otomatik kopyalar
- ✅ WSL kurulum scriptleri ekler

**Çıktı Konumları:**
1. WSL içinde: `/home/username/ffpas/ffpas_export_*.tar.gz`
2. Windows Desktop: `C:\Users\YourName\Desktop\ffpas_export_*.tar.gz`

---

## 🚀 Yeni PC'de Kurulum

### Seçenek 1: WSL Ubuntu'da Kurulum (Önerilen)

```bash
# 1. Arşivi WSL'e kopyala
# Windows'tan WSL'e:
# Dosyayı WSL home dizinine sürükle veya:
cp /mnt/c/Users/YourName/Desktop/ffpas_export_*.tar.gz ~/

# 2. Arşivi çıkart
cd ~
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 3. Hızlı kurulum
chmod +x wsl_quick_setup.sh
./wsl_quick_setup.sh
```

**Kurulum süresi:** 5-10 dakika

### Seçenek 2: Manuel Kurulum

```bash
# 1. Arşivi çıkart
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. WSL kurulum scriptini çalıştır
chmod +x wsl_install.sh
./wsl_install.sh

# 3. Yapılandır
nano .env

# 4. Başlat
python start.py
```

---

## 🔗 Windows Entegrasyonu

### WSL'den Windows'a Erişim

```bash
# Windows C: sürücüsü
cd /mnt/c/

# Windows Desktop
cd /mnt/c/Users/YourName/Desktop/

# Dosya kopyalama
cp file.txt /mnt/c/Users/YourName/Desktop/
```

### Windows'tan WSL'e Erişim

**File Explorer'da:**
```
\\wsl$\Ubuntu-22.04\home\username\ffpas
```

**PowerShell'de:**
```powershell
cd \\wsl$\Ubuntu-22.04\home\username\ffpas
```

### Port Erişimi

WSL2 otomatik olarak portları Windows'a forward eder:
- WSL'de: `http://localhost:5000`
- Windows'ta: `http://localhost:5000`
- Aynı port, ek yapılandırma gerekmez!

---

## 🛠️ WSL Özel Komutlar

### WSL Servisleri

```bash
# Redis başlat
sudo service redis-server start

# Redis durumu
sudo service redis-server status

# Redis durdur
sudo service redis-server stop
```

### WSL Yeniden Başlatma

**PowerShell'de (Windows):**
```powershell
# WSL'i kapat
wsl --shutdown

# Belirli distro'yu kapat
wsl --terminate Ubuntu-22.04

# WSL'i başlat
wsl
```

### WSL Kaynak Yönetimi

**`.wslconfig` dosyası oluştur (Windows):**
```
C:\Users\YourName\.wslconfig
```

**İçerik:**
```ini
[wsl2]
memory=4GB
processors=2
swap=2GB
```

---

## 📊 Performans İpuçları

### 1. Dosyaları WSL Filesystem'de Tut

**Hızlı (WSL filesystem):**
```bash
/home/username/ffpas/
```

**Yavaş (Windows filesystem):**
```bash
/mnt/c/Users/YourName/ffpas/
```

**Neden?** WSL filesystem 5-10x daha hızlı!

### 2. WSL2 Kullan (WSL1 Değil)

**Kontrol et:**
```powershell
wsl --list --verbose
```

**WSL2'ye geçiş:**
```powershell
wsl --set-version Ubuntu-22.04 2
```

### 3. Yeterli Bellek Ayır

`.wslconfig` ile en az 4GB RAM ayırın.

---

## 🐳 Docker ile WSL

### Docker Desktop (Önerilen)

1. Docker Desktop for Windows'u yükle
2. Settings → Resources → WSL Integration
3. Ubuntu-22.04'ü etkinleştir

**Kullanım:**
```bash
cd ffpas_export_*
docker-compose up -d
```

### Docker Engine (Alternatif)

```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER

# Yeniden giriş yap
exit
# WSL'i yeniden aç

# Docker başlat
sudo service docker start

# Kullanım
docker-compose up -d
```

---

## 🔧 Sorun Giderme

### "Permission denied" Hatası

```bash
# Script izinlerini düzelt
chmod +x *.sh

# Veya sudo ile çalıştır
sudo ./wsl_export.sh
```

### Python Bulunamadı

```bash
# Python kurulumu
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Port Zaten Kullanımda

```bash
# Hangi process kullanıyor?
sudo lsof -i :5000

# Process'i durdur
sudo kill -9 <PID>

# Veya farklı port kullan
# .env dosyasında PORT=5001
```

### Redis Bağlantı Hatası

```bash
# Redis kurulumu
sudo apt install redis-server

# Redis başlat
sudo service redis-server start

# Otomatik başlatma
sudo systemctl enable redis-server
```

### WSL Ağ Sorunları

**PowerShell'de (Yönetici):**
```powershell
# WSL'i yeniden başlat
wsl --shutdown
wsl

# Veya Windows'u yeniden başlat
```

### Disk Alanı Yetersiz

```bash
# Disk kullanımını kontrol et
df -h

# Büyük dosyaları bul
du -h --max-depth=1 | sort -hr

# Temizlik
sudo apt autoremove
sudo apt clean
```

---

## 📁 Dosya Yapısı

### WSL'de Önerilen Konum

```
/home/username/
└── ffpas/
    ├── ai/
    ├── api/
    ├── database/
    ├── data/
    ├── venv/
    └── ...
```

### Windows'tan Erişim

```
\\wsl$\Ubuntu-22.04\home\username\ffpas\
```

---

## 🚀 Hızlı Komutlar

### Export

```bash
./wsl_export.sh
```

### Kurulum

```bash
./wsl_quick_setup.sh
```

### Başlatma

```bash
# Geliştirme
python start.py

# Production
python demo_api.py

# Docker
docker-compose up -d
```

### Durdurma

```bash
# Ctrl+C (terminal)

# Docker
docker-compose down
```

---

## 🔄 Transfer Senaryoları

### Senaryo 1: WSL → WSL

```bash
# Kaynak PC (WSL)
./wsl_export.sh
# Arşiv Windows Desktop'a kopyalanır

# Hedef PC (WSL)
cp /mnt/c/Users/YourName/Desktop/ffpas_export_*.tar.gz ~/
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*
./wsl_quick_setup.sh
```

### Senaryo 2: WSL → Linux

```bash
# Kaynak PC (WSL)
./wsl_export.sh

# Arşivi Linux'a kopyala (SCP, USB, vb.)
scp ffpas_export_*.tar.gz user@linux-pc:/home/user/

# Hedef PC (Linux)
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*
./install.sh
```

### Senaryo 3: WSL → Windows Native

```bash
# Kaynak PC (WSL)
./wsl_export.sh

# Windows'ta çıkart ve install.bat çalıştır
```

---

## 💡 İpuçları

### 1. Hızlı Erişim

**Windows Terminal'de profil ekle:**
```json
{
  "name": "FFPAS",
  "commandline": "wsl -d Ubuntu-22.04 -- bash -c 'cd ~/ffpas && bash'",
  "startingDirectory": "//wsl$/Ubuntu-22.04/home/username/ffpas"
}
```

### 2. Alias Oluştur

**~/.bashrc'ye ekle:**
```bash
alias ffpas='cd ~/ffpas && source venv/bin/activate'
alias ffpas-start='cd ~/ffpas && python start.py'
alias ffpas-export='cd ~/ffpas && ./wsl_export.sh'
```

**Kullanım:**
```bash
ffpas          # Dizine git ve venv aktif et
ffpas-start    # Sunucuyu başlat
ffpas-export   # Export yap
```

### 3. Otomatik Başlatma

**~/.bashrc'ye ekle:**
```bash
# FFPAS otomatik başlat (opsiyonel)
if [ -f ~/ffpas/venv/bin/activate ]; then
    cd ~/ffpas
    source venv/bin/activate
fi
```

---

## 📞 Destek

### Logları Kontrol Et

```bash
# Uygulama logları
tail -f logs/app.log

# WSL logları
dmesg | tail

# Sistem logları
sudo journalctl -xe
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Detaylı Bilgi

- `README_V2.md` - Ana dokümantasyon
- `TRANSFER_GUIDE.md` - Genel transfer kılavuzu
- `UPGRADE_GUIDE.md` - Upgrade rehberi

---

## ✅ Kontrol Listesi

### Export Öncesi
- [ ] Tüm değişiklikler kaydedildi
- [ ] Veritabanı güncel
- [ ] Model dosyaları mevcut
- [ ] WSL çalışıyor

### Export Sonrası
- [ ] Arşiv oluşturuldu
- [ ] Windows Desktop'a kopyalandı
- [ ] Boyut makul (100-300 MB)
- [ ] Arşiv test edildi

### Kurulum Öncesi
- [ ] WSL2 kurulu
- [ ] Ubuntu-22.04 yüklü
- [ ] Yeterli disk alanı (1GB+)
- [ ] İnternet bağlantısı var

### Kurulum Sonrası
- [ ] Health check başarılı
- [ ] API docs açılıyor
- [ ] Windows'tan erişilebiliyor
- [ ] Test prediction çalışıyor

---

## 🎉 Başarı!

WSL Ubuntu'da FFPAS v2.0 çalışıyor!

**Erişim:**
- WSL: `http://localhost:5000`
- Windows: `http://localhost:5000`
- API Docs: `http://localhost:5000/api/docs`

**Kolay gelsin! 🚀**
