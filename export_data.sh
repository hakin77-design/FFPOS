#!/bin/bash
# FFPAS Data Export Script
# Bu script tüm gerekli dosyaları ve verileri yedekler

set -e

echo "=========================================="
echo "FFPAS Data Export Script"
echo "=========================================="

# Tarih damgası
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_DIR="ffpas_export_${TIMESTAMP}"
ARCHIVE_NAME="${EXPORT_DIR}.tar.gz"

echo "Export directory: ${EXPORT_DIR}"
echo "Archive name: ${ARCHIVE_NAME}"

# Export dizinini oluştur
mkdir -p "${EXPORT_DIR}"

echo ""
echo "1. Copying application files..."
# Uygulama dosyalarını kopyala
cp -r ai "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: ai directory not found"
cp -r api "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: api directory not found"
cp -r database "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: database directory not found"
cp -r utils "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: utils directory not found"
cp -r tests "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: tests directory not found"
cp -r frontend "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: frontend directory not found"

echo "2. Copying configuration files..."
# Yapılandırma dosyaları
cp config.py "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: config.py not found"
cp requirements.txt "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: requirements.txt not found"
cp .env.example "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: .env.example not found"
cp .gitignore "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: .gitignore not found"
cp Dockerfile "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: Dockerfile not found"
cp docker-compose.yml "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: docker-compose.yml not found"
cp Makefile "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: Makefile not found"
cp pytest.ini "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: pytest.ini not found"
cp start.py "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: start.py not found"

echo "3. Copying documentation..."
# Dokümantasyon
cp README*.md "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: README files not found"
cp ANALIZ_RAPORU.md "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: ANALIZ_RAPORU.md not found"
cp UPGRADE_GUIDE.md "${EXPORT_DIR}/" 2>/dev/null || echo "Warning: UPGRADE_GUIDE.md not found"

echo "4. Copying data files..."
# Data dizinini oluştur
mkdir -p "${EXPORT_DIR}/data"

# Veritabanı dosyası varsa kopyala
if [ -f "data/matches.db" ]; then
    echo "   - Copying SQLite database..."
    cp data/matches.db "${EXPORT_DIR}/data/"
    echo "   ✓ Database copied"
else
    echo "   - No SQLite database found, copying JSON files..."
    # JSON dosyalarını kopyala
    cp data/*.json "${EXPORT_DIR}/data/" 2>/dev/null || echo "   Warning: No JSON files found"
fi

# Teams.json varsa kopyala
if [ -f "data/teams.json" ]; then
    cp data/teams.json "${EXPORT_DIR}/data/"
    echo "   ✓ teams.json copied"
fi

echo "5. Copying model files..."
# Model dosyaları
if [ -f "ai_model.pt" ]; then
    cp ai_model.pt "${EXPORT_DIR}/"
    echo "   ✓ ai_model.pt copied"
else
    echo "   Warning: ai_model.pt not found"
fi

if [ -f "goals_model.pt" ]; then
    cp goals_model.pt "${EXPORT_DIR}/"
    echo "   ✓ goals_model.pt copied"
fi

echo "6. Creating installation scripts..."
# Kurulum scriptlerini oluştur
cat > "${EXPORT_DIR}/install.sh" << 'INSTALL_EOF'
#!/bin/bash
# FFPAS Installation Script for Linux/macOS

set -e

echo "=========================================="
echo "FFPAS v2.0 Installation"
echo "=========================================="

# Python version check
echo "1. Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Python version: ${PYTHON_VERSION}"

# Virtual environment
echo ""
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "4. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✓ Dependencies installed"

# Create directories
echo ""
echo "5. Creating directories..."
mkdir -p logs
mkdir -p data
echo "   ✓ Directories created"

# Environment configuration
echo ""
echo "6. Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "   ✓ .env file created"
    echo "   ⚠ Please edit .env file with your configuration"
else
    echo "   ✓ .env file already exists"
fi

# Database setup
echo ""
echo "7. Database setup..."
if [ -f "data/matches.db" ]; then
    echo "   ✓ Database already exists (migrated data)"
else
    echo "   ⚠ No database found"
    echo "   You need to run migration:"
    echo "   python database/migrate.py"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. If no database exists, run: python database/migrate.py"
echo "3. Start the server: python start.py"
echo ""
echo "Or use Docker:"
echo "docker-compose up -d"
echo ""
INSTALL_EOF

chmod +x "${EXPORT_DIR}/install.sh"

# Windows kurulum scripti
cat > "${EXPORT_DIR}/install.bat" << 'INSTALL_BAT_EOF'
@echo off
REM FFPAS Installation Script for Windows

echo ==========================================
echo FFPAS v2.0 Installation
echo ==========================================

REM Python version check
echo 1. Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

python --version

REM Virtual environment
echo.
echo 2. Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo    √ Virtual environment created
) else (
    echo    √ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 3. Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 4. Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo    √ Dependencies installed

REM Create directories
echo.
echo 5. Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo    √ Directories created

REM Environment configuration
echo.
echo 6. Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo    √ .env file created
    echo    ⚠ Please edit .env file with your configuration
) else (
    echo    √ .env file already exists
)

REM Database setup
echo.
echo 7. Database setup...
if exist "data\matches.db" (
    echo    √ Database already exists (migrated data)
) else (
    echo    ⚠ No database found
    echo    You need to run migration:
    echo    python database\migrate.py
)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. If no database exists, run: python database\migrate.py
echo 3. Start the server: python start.py
echo.
echo Or use Docker:
echo docker-compose up -d
echo.
pause
INSTALL_BAT_EOF

# README dosyası
cat > "${EXPORT_DIR}/INSTALLATION.md" << 'README_EOF'
# FFPAS v2.0 - Installation Guide

## 📦 Package Contents

This package contains:
- Complete FFPAS v2.0 application
- All source code
- Data files (database or JSON)
- AI model files
- Configuration templates
- Installation scripts

## 🖥️ System Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.10 or higher
- **RAM**: 2GB minimum
- **Disk**: 1GB free space
- **Optional**: Redis (for caching)

## 🚀 Quick Installation

### Linux / macOS

```bash
# 1. Extract archive
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. Run installation script
chmod +x install.sh
./install.sh

# 3. Configure environment
nano .env

# 4. Start server
source venv/bin/activate
python start.py
```

### Windows

```cmd
# 1. Extract archive (use 7-Zip or WinRAR)

# 2. Run installation script
install.bat

# 3. Configure environment
notepad .env

# 4. Start server
venv\Scripts\activate
python start.py
```

## 🐳 Docker Installation (Recommended)

```bash
# 1. Extract archive
tar -xzf ffpas_export_*.tar.gz
cd ffpas_export_*

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Start with Docker
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

## 📝 Configuration

Edit `.env` file:

```bash
# API Keys (optional)
FOOTBALL_API_KEY=your_key_here
RAPIDAPI_KEY=your_key_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/matches.db

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Server
PORT=5000
DEBUG=False
```

## 🗄️ Database Setup

### If database file exists (matches.db)
No action needed! Database is already migrated.

### If only JSON files exist
Run migration:

```bash
python database/migrate.py
```

This will:
- Create SQLite database
- Import all JSON data
- Calculate team statistics
- Takes 5-10 minutes

## ✅ Verification

```bash
# Check health
curl http://localhost:5000/api/health

# Open API docs
open http://localhost:5000/api/docs

# Test prediction
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

## 🔧 Troubleshooting

### Port already in use
Change port in `.env`:
```
PORT=5001
```

### Python not found
Install Python 3.10+:
- Linux: `sudo apt install python3.10`
- macOS: `brew install python@3.10`
- Windows: Download from python.org

### Module not found
```bash
pip install -r requirements.txt
```

### Database error
Reset database:
```bash
rm data/matches.db
python database/migrate.py
```

## 📚 Documentation

- Main README: `README_V2.md`
- Upgrade Guide: `UPGRADE_GUIDE.md`
- Analysis Report: `ANALIZ_RAPORU.md`
- API Docs: http://localhost:5000/api/docs

## 🆘 Support

For issues:
1. Check logs: `tail -f logs/app.log`
2. Check health: `curl http://localhost:5000/api/health/detailed`
3. Review documentation

## 🎉 Success!

If you see:
```
✓ Database initialized
✓ Redis connected (or disabled)
✓ Model loaded
Server running on http://0.0.0.0:5000
```

You're ready to go! 🚀
README_EOF

echo ""
echo "7. Creating archive..."
# Arşiv oluştur
tar -czf "${ARCHIVE_NAME}" "${EXPORT_DIR}"

# Boyut bilgisi
ARCHIVE_SIZE=$(du -h "${ARCHIVE_NAME}" | cut -f1)

echo ""
echo "=========================================="
echo "Export Complete!"
echo "=========================================="
echo "Archive: ${ARCHIVE_NAME}"
echo "Size: ${ARCHIVE_SIZE}"
echo ""
echo "Contents:"
echo "  - Application code"
echo "  - Data files"
echo "  - Model files"
echo "  - Configuration templates"
echo "  - Installation scripts"
echo "  - Documentation"
echo ""
echo "To install on another PC:"
echo "1. Copy ${ARCHIVE_NAME} to target PC"
echo "2. Extract: tar -xzf ${ARCHIVE_NAME}"
echo "3. cd ${EXPORT_DIR}"
echo "4. Run: ./install.sh (Linux/Mac) or install.bat (Windows)"
echo ""
echo "Cleaning up temporary directory..."
rm -rf "${EXPORT_DIR}"
echo "Done!"
