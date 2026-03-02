#!/bin/bash
# FFPAS Export Script for WSL Ubuntu
# Bu script WSL ortamında çalışır ve Windows'a erişilebilir bir konuma export eder

set -e

echo "=========================================="
echo "FFPAS WSL Ubuntu Export Script"
echo "=========================================="

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Tarih damgası
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="ffpas_export_${TIMESTAMP}"
ARCHIVE_NAME="${EXPORT_DIR}.tar.gz"

echo -e "${BLUE}Export directory: ${EXPORT_DIR}${NC}"
echo -e "${BLUE}Archive name: ${ARCHIVE_NAME}${NC}"

# Export dizinini oluştur
mkdir -p "${EXPORT_DIR}"

echo ""
echo -e "${YELLOW}[1/8] Copying application files...${NC}"
# Uygulama dosyalarını kopyala
for dir in ai api database utils tests frontend; do
    if [ -d "$dir" ]; then
        cp -r "$dir" "${EXPORT_DIR}/" 2>/dev/null && echo -e "${GREEN}  ✓ $dir/${NC}" || echo -e "${YELLOW}  ⚠ $dir/ not found${NC}"
    fi
done

echo ""
echo -e "${YELLOW}[2/8] Copying configuration files...${NC}"
# Yapılandırma dosyaları
for file in config.py requirements.txt .env.example .gitignore Dockerfile docker-compose.yml Makefile pytest.ini start.py; do
    if [ -f "$file" ]; then
        cp "$file" "${EXPORT_DIR}/" && echo -e "${GREEN}  ✓ $file${NC}"
    fi
done

echo ""
echo -e "${YELLOW}[3/8] Copying documentation...${NC}"
# Dokümantasyon
for file in README*.md ANALIZ_RAPORU.md UPGRADE_GUIDE.md TRANSFER_GUIDE.md KURULUM_SCRIPTLERI.md DEMO_RESULTS.md; do
    if [ -f "$file" ]; then
        cp "$file" "${EXPORT_DIR}/" && echo -e "${GREEN}  ✓ $file${NC}"
    fi
done

echo ""
echo -e "${YELLOW}[4/8] Copying data files...${NC}"
# Data dizinini oluştur
mkdir -p "${EXPORT_DIR}/data"

# Veritabanı dosyası varsa kopyala
if [ -f "data/matches.db" ]; then
    echo -e "${BLUE}  → Copying SQLite database...${NC}"
    cp data/matches.db "${EXPORT_DIR}/data/"
    DB_SIZE=$(du -h data/matches.db | cut -f1)
    echo -e "${GREEN}  ✓ Database copied (${DB_SIZE})${NC}"
else
    echo -e "${YELLOW}  ⚠ No SQLite database found${NC}"
    # JSON dosyalarını kopyala
    JSON_COUNT=$(ls -1 data/*.json 2>/dev/null | wc -l)
    if [ $JSON_COUNT -gt 0 ]; then
        echo -e "${BLUE}  → Copying ${JSON_COUNT} JSON files...${NC}"
        cp data/*.json "${EXPORT_DIR}/data/" 2>/dev/null
        echo -e "${GREEN}  ✓ JSON files copied${NC}"
    else
        echo -e "${YELLOW}  ⚠ No data files found${NC}"
    fi
fi

# Teams.json varsa kopyala
if [ -f "data/teams.json" ]; then
    cp data/teams.json "${EXPORT_DIR}/data/"
    echo -e "${GREEN}  ✓ teams.json copied${NC}"
fi

echo ""
echo -e "${YELLOW}[5/8] Copying model files...${NC}"
# Model dosyaları
if [ -f "ai_model.pt" ]; then
    MODEL_SIZE=$(du -h ai_model.pt | cut -f1)
    cp ai_model.pt "${EXPORT_DIR}/"
    echo -e "${GREEN}  ✓ ai_model.pt copied (${MODEL_SIZE})${NC}"
else
    echo -e "${YELLOW}  ⚠ ai_model.pt not found${NC}"
fi

if [ -f "goals_model.pt" ]; then
    cp goals_model.pt "${EXPORT_DIR}/"
    echo -e "${GREEN}  ✓ goals_model.pt copied${NC}"
fi

if [ -f "ai_model_data_raw.pt" ]; then
    cp ai_model_data_raw.pt "${EXPORT_DIR}/"
    echo -e "${GREEN}  ✓ ai_model_data_raw.pt copied${NC}"
fi

echo ""
echo -e "${YELLOW}[6/8] Creating installation scripts...${NC}"

# WSL için özel kurulum scripti
cat > "${EXPORT_DIR}/wsl_install.sh" << 'WSL_INSTALL_EOF'
#!/bin/bash
# FFPAS Installation Script for WSL Ubuntu

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "FFPAS v2.0 Installation for WSL Ubuntu"
echo "=========================================="

# Python version check
echo -e "\n${BLUE}[1/7] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is not installed${NC}"
    echo "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"

# Virtual environment
echo -e "\n${BLUE}[2/7] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "\n${BLUE}[3/7] Installing dependencies...${NC}"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create directories
echo -e "\n${BLUE}[4/7] Creating directories...${NC}"
mkdir -p logs data
echo -e "${GREEN}✓ Directories created${NC}"

# Environment configuration
echo -e "\n${BLUE}[5/7] Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Database setup
echo -e "\n${BLUE}[6/7] Database setup...${NC}"
if [ -f "data/matches.db" ]; then
    DB_SIZE=$(du -h data/matches.db | cut -f1)
    echo -e "${GREEN}✓ Database already exists (${DB_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠ No database found${NC}"
    echo "You need to run migration:"
    echo "  python database/migrate.py"
fi

# Permissions
echo -e "\n${BLUE}[7/7] Setting permissions...${NC}"
chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Permissions set${NC}"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. If no database: python database/migrate.py"
echo "3. Start server: python start.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
WSL_INSTALL_EOF

chmod +x "${EXPORT_DIR}/wsl_install.sh"
echo -e "${GREEN}  ✓ wsl_install.sh created${NC}"

# Linux kurulum scripti
cat > "${EXPORT_DIR}/install.sh" << 'INSTALL_EOF'
#!/bin/bash
# FFPAS Installation Script for Linux

set -e

echo "=========================================="
echo "FFPAS v2.0 Installation"
echo "=========================================="

# Python check
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi
python3 --version

# Virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs data

# Environment
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created"
fi

# Database check
if [ -f "data/matches.db" ]; then
    echo "✓ Database exists"
else
    echo "⚠ No database - run: python database/migrate.py"
fi

echo ""
echo "Installation complete!"
echo "Start server: python start.py"
INSTALL_EOF

chmod +x "${EXPORT_DIR}/install.sh"
echo -e "${GREEN}  ✓ install.sh created${NC}"

# README
cat > "${EXPORT_DIR}/WSL_INSTALLATION.md" << 'README_EOF'
# FFPAS v2.0 - WSL Ubuntu Installation

## Quick Start

```bash
# 1. Extract archive
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. Run WSL installation
chmod +x wsl_install.sh
./wsl_install.sh

# 3. Configure
nano .env

# 4. Start server
python start.py
```

## Access from Windows

The server will be accessible from Windows at:
- http://localhost:5000
- http://127.0.0.1:5000

## WSL Specific Notes

### File Permissions
```bash
chmod +x *.sh
```

### Python Installation
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Redis (Optional)
```bash
sudo apt install redis-server
sudo service redis-server start
```

### Port Access
WSL2 automatically forwards ports to Windows.
No additional configuration needed.

## Troubleshooting

### Permission Denied
```bash
chmod +x wsl_install.sh
./wsl_install.sh
```

### Python Not Found
```bash
sudo apt install python3
```

### Port Already in Use
Edit .env and change PORT=5001

## Windows Integration

### Access WSL Files from Windows
```
\\wsl$\Ubuntu-22.04\home\username\ffpas
```

### Copy to Windows
```bash
cp ffpas_export_*.tar.gz /mnt/c/Users/YourName/Desktop/
```

## Docker in WSL

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Start with Docker
docker-compose up -d
```

## Performance Tips

1. Keep files in WSL filesystem (faster)
2. Use WSL2 (not WSL1)
3. Allocate enough memory in .wslconfig

## Support

See README_V2.md for full documentation.
README_EOF

echo -e "${GREEN}  ✓ WSL_INSTALLATION.md created${NC}"

echo ""
echo -e "${YELLOW}[7/8] Creating archive...${NC}"
# Arşiv oluştur
tar -czf "${ARCHIVE_NAME}" "${EXPORT_DIR}"

# Boyut bilgisi
ARCHIVE_SIZE=$(du -h "${ARCHIVE_NAME}" | cut -f1)

echo ""
echo -e "${YELLOW}[8/8] Copying to Windows accessible location...${NC}"

# Windows Desktop'a kopyala (opsiyonel)
WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
if [ ! -z "$WINDOWS_USER" ]; then
    DESKTOP_PATH="/mnt/c/Users/${WINDOWS_USER}/Desktop"
    if [ -d "$DESKTOP_PATH" ]; then
        cp "${ARCHIVE_NAME}" "$DESKTOP_PATH/"
        echo -e "${GREEN}  ✓ Copied to Windows Desktop${NC}"
        echo -e "${BLUE}  → ${DESKTOP_PATH}/${ARCHIVE_NAME}${NC}"
    fi
fi

# Mevcut dizinde de bırak
echo -e "${GREEN}  ✓ Archive in current directory${NC}"
echo -e "${BLUE}  → $(pwd)/${ARCHIVE_NAME}${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Export Complete!${NC}"
echo "=========================================="
echo -e "${BLUE}Archive: ${ARCHIVE_NAME}${NC}"
echo -e "${BLUE}Size: ${ARCHIVE_SIZE}${NC}"
echo ""
echo "Contents:"
echo "  ✓ Application code"
echo "  ✓ Data files"
echo "  ✓ Model files"
echo "  ✓ Configuration templates"
echo "  ✓ WSL installation script"
echo "  ✓ Documentation"
echo ""
echo "Archive locations:"
echo "  1. Current directory: $(pwd)"
if [ ! -z "$WINDOWS_USER" ] && [ -d "/mnt/c/Users/${WINDOWS_USER}/Desktop" ]; then
    echo "  2. Windows Desktop: C:\\Users\\${WINDOWS_USER}\\Desktop"
fi
echo ""
echo "To install on another PC:"
echo "  1. Copy ${ARCHIVE_NAME} to target PC"
echo "  2. Extract: tar -xzf ${ARCHIVE_NAME}"
echo "  3. cd ${EXPORT_DIR}"
echo "  4. Run: ./wsl_install.sh"
echo ""
echo "Cleaning up temporary directory..."
rm -rf "${EXPORT_DIR}"
echo -e "${GREEN}Done!${NC}"
