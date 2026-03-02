#!/bin/bash
# FFPAS Quick Setup Script for WSL Ubuntu
# Tek komutla tüm kurulumu yapar

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗███████╗██████╗  █████╗ ███████╗              ║
║   ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝              ║
║   █████╗  █████╗  ██████╔╝███████║███████╗              ║
║   ██╔══╝  ██╔══╝  ██╔═══╝ ██╔══██║╚════██║              ║
║   ██║     ██║     ██║     ██║  ██║███████║              ║
║   ╚═╝     ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝              ║
║                                                           ║
║   Quick Setup for WSL Ubuntu v2.0                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo "This script will:"
echo "  1. Check system requirements"
echo "  2. Install Python dependencies"
echo "  3. Setup environment configuration"
echo "  4. Create necessary directories"
echo "  5. Optionally run database migration"
echo "  6. Start the server"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 1: System Requirements Check${NC}"
echo "=========================================="

# Check Python
echo -e "\n${YELLOW}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo -e "${YELLOW}Installing Python 3...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    echo -e "${GREEN}✓ Python 3 installed${NC}"
fi

# Check pip
echo -e "\n${YELLOW}Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ pip ${PIP_VERSION}${NC}"
else
    echo -e "${YELLOW}Installing pip...${NC}"
    sudo apt install -y python3-pip
fi

# Check Redis (optional)
echo -e "\n${YELLOW}Checking Redis...${NC}"
if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✓ Redis is installed (caching enabled)${NC}"
else
    echo -e "${YELLOW}⚠ Redis not installed (caching will be disabled)${NC}"
    read -p "Install Redis? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt install -y redis-server
        sudo service redis-server start
        echo -e "${GREEN}✓ Redis installed and started${NC}"
    fi
fi

# WSL Version
echo -e "\n${YELLOW}WSL Information:${NC}"
if [ -f /proc/version ]; then
    WSL_VERSION=$(grep -oP 'WSL\K[0-9]+' /proc/version 2>/dev/null || echo "1")
    echo -e "${BLUE}  WSL Version: ${WSL_VERSION}${NC}"
fi

# Windows User
WINDOWS_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r')
if [ ! -z "$WINDOWS_USER" ]; then
    echo -e "${BLUE}  Windows User: ${WINDOWS_USER}${NC}"
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 2: Virtual Environment${NC}"
echo "=========================================="

if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
    read -p "Recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo "=========================================="
echo -e "${BLUE}Step 3: Installing Dependencies${NC}"
echo "=========================================="

echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip -q

echo -e "${YELLOW}Installing requirements (this may take a few minutes)...${NC}"
if pip install -r requirements.txt -q; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install some dependencies${NC}"
    echo "Try manually: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 4: Directory Setup${NC}"
echo "=========================================="

mkdir -p logs
echo -e "${GREEN}✓ logs/ directory created${NC}"

mkdir -p data
echo -e "${GREEN}✓ data/ directory created${NC}"

echo ""
echo "=========================================="
echo -e "${BLUE}Step 5: Environment Configuration${NC}"
echo "=========================================="

if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file already exists${NC}"
    read -p "Overwrite with template? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from template${NC}"
    fi
else
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
fi

echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
read -p "Edit .env now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ${EDITOR:-nano} .env
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 6: Database Setup${NC}"
echo "=========================================="

if [ -f "data/matches.db" ]; then
    DB_SIZE=$(du -h data/matches.db | cut -f1)
    echo -e "${GREEN}✓ Database already exists (${DB_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠ No database found${NC}"
    
    # Check if JSON files exist
    JSON_COUNT=$(ls -1 data/*.json 2>/dev/null | wc -l)
    if [ $JSON_COUNT -gt 0 ]; then
        echo -e "${BLUE}Found ${JSON_COUNT} JSON data files${NC}"
        read -p "Run database migration now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Starting migration (this may take 5-10 minutes)...${NC}"
            if python database/migrate.py; then
                echo -e "${GREEN}✓ Database migration completed${NC}"
            else
                echo -e "${RED}✗ Migration failed${NC}"
                echo "You can run it later: python database/migrate.py"
            fi
        else
            echo -e "${YELLOW}⚠ Skipping migration${NC}"
            echo "Run later: python database/migrate.py"
        fi
    else
        echo -e "${YELLOW}⚠ No data files found${NC}"
        echo "You'll need to add data files to data/ directory"
    fi
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 7: Model Files${NC}"
echo "=========================================="

if [ -f "ai_model.pt" ]; then
    MODEL_SIZE=$(du -h ai_model.pt | cut -f1)
    echo -e "${GREEN}✓ AI model found (${MODEL_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠ AI model not found (ai_model.pt)${NC}"
    echo "The system will work with reduced accuracy"
fi

echo ""
echo "=========================================="
echo -e "${BLUE}Step 8: Permissions${NC}"
echo "=========================================="

chmod +x *.sh 2>/dev/null || true
echo -e "${GREEN}✓ Script permissions set${NC}"

echo ""
echo "=========================================="
echo -e "${BLUE}Step 9: Running Tests${NC}"
echo "=========================================="

read -p "Run tests to verify installation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running tests...${NC}"
    if pytest tests/ -v --tb=short 2>/dev/null; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed (this may be normal if data is not migrated)${NC}"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Installation Summary${NC}"
echo "=========================================="

echo -e "${GREEN}✓ Python environment: Ready${NC}"
echo -e "${GREEN}✓ Dependencies: Installed${NC}"
echo -e "${GREEN}✓ Configuration: Created${NC}"
echo -e "${GREEN}✓ Directories: Created${NC}"

if [ -f "data/matches.db" ]; then
    echo -e "${GREEN}✓ Database: Ready${NC}"
else
    echo -e "${YELLOW}⚠ Database: Not migrated${NC}"
fi

if [ -f "ai_model.pt" ]; then
    echo -e "${GREEN}✓ AI Model: Available${NC}"
else
    echo -e "${YELLOW}⚠ AI Model: Not found${NC}"
fi

echo ""
echo "=========================================="
echo -e "${CYAN}Next Steps${NC}"
echo "=========================================="

echo ""
echo "1. Review configuration:"
echo "   nano .env"
echo ""
echo "2. If database not migrated:"
echo "   python database/migrate.py"
echo ""
echo "3. Start the server:"
echo "   python start.py"
echo ""
echo "4. Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "5. Access from Windows:"
echo "   Frontend: http://localhost:5000"
echo "   API Docs: http://localhost:5000/api/docs"
echo "   Health: http://localhost:5000/api/health"
echo ""

# WSL specific info
if [ ! -z "$WINDOWS_USER" ]; then
    echo "=========================================="
    echo -e "${CYAN}WSL Integration${NC}"
    echo "=========================================="
    echo ""
    echo "Access files from Windows:"
    echo "  \\\\wsl\$\\Ubuntu-22.04$(pwd)"
    echo ""
    echo "Copy to Windows Desktop:"
    echo "  cp file.txt /mnt/c/Users/${WINDOWS_USER}/Desktop/"
    echo ""
fi

read -p "Start server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}Starting FFPAS server...${NC}"
    echo ""
    python start.py
else
    echo ""
    echo -e "${GREEN}Setup complete! Run 'python start.py' when ready.${NC}"
    echo ""
fi
