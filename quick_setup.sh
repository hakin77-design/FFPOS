#!/bin/bash
# FFPAS Quick Setup Script
# Tek komutla tüm kurulumu yapar

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║   ███████╗███████╗██████╗  █████╗ ███████╗              ║"
    echo "║   ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝              ║"
    echo "║   █████╗  █████╗  ██████╔╝███████║███████╗              ║"
    echo "║   ██╔══╝  ██╔══╝  ██╔═══╝ ██╔══██║╚════██║              ║"
    echo "║   ██║     ██║     ██║     ██║  ██║███████║              ║"
    echo "║   ╚═╝     ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝              ║"
    echo "║                                                           ║"
    echo "║   Quick Setup Script v2.0                                ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

print_header

echo ""
echo "This script will:"
echo "1. Check system requirements"
echo "2. Install Python dependencies"
echo "3. Setup environment configuration"
echo "4. Create necessary directories"
echo "5. Optionally run database migration"
echo "6. Start the server"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Step 1: System Requirements Check"
echo "=========================================="

# Check Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Python version: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not installed"
    echo "Please install Python 3.10 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3.10"
    echo "  macOS: brew install python@3.10"
    exit 1
fi

# Check pip
if check_command pip3; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_info "pip version: $PIP_VERSION"
else
    print_warning "pip not found, installing..."
    python3 -m ensurepip --upgrade
fi

# Check git (optional)
if check_command git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_info "git version: $GIT_VERSION"
else
    print_warning "git not installed (optional)"
fi

# Check Redis (optional)
if check_command redis-server; then
    print_success "Redis is installed (caching enabled)"
else
    print_warning "Redis not installed (caching will be disabled)"
    print_info "To install Redis:"
    print_info "  Ubuntu/Debian: sudo apt install redis-server"
    print_info "  macOS: brew install redis"
fi

echo ""
echo "=========================================="
echo "Step 2: Virtual Environment"
echo "=========================================="

if [ -d "venv" ]; then
    print_info "Virtual environment already exists"
    read -p "Recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

echo ""
echo "=========================================="
echo "Step 3: Installing Dependencies"
echo "=========================================="

print_info "Upgrading pip..."
pip install --upgrade pip -q

print_info "Installing requirements (this may take a few minutes)..."
if pip install -r requirements.txt -q; then
    print_success "All dependencies installed"
else
    print_error "Failed to install some dependencies"
    print_info "Try manually: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 4: Directory Setup"
echo "=========================================="

mkdir -p logs
print_success "logs/ directory created"

mkdir -p data
print_success "data/ directory created"

echo ""
echo "=========================================="
echo "Step 5: Environment Configuration"
echo "=========================================="

if [ -f ".env" ]; then
    print_info ".env file already exists"
    read -p "Overwrite with template? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        print_success ".env file created from template"
    fi
else
    cp .env.example .env
    print_success ".env file created from template"
fi

print_warning "Please edit .env file with your configuration"
print_info "Required settings:"
print_info "  - API keys (if using external APIs)"
print_info "  - Database URL"
print_info "  - Redis configuration"

read -p "Edit .env now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ${EDITOR:-nano} .env
fi

echo ""
echo "=========================================="
echo "Step 6: Database Setup"
echo "=========================================="

if [ -f "data/matches.db" ]; then
    print_success "Database already exists"
    DB_SIZE=$(du -h data/matches.db | cut -f1)
    print_info "Database size: $DB_SIZE"
else
    print_warning "No database found"
    
    # Check if JSON files exist
    JSON_COUNT=$(ls -1 data/*.json 2>/dev/null | wc -l)
    if [ $JSON_COUNT -gt 0 ]; then
        print_info "Found $JSON_COUNT JSON data files"
        read -p "Run database migration now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Starting migration (this may take 5-10 minutes)..."
            if python database/migrate.py; then
                print_success "Database migration completed"
            else
                print_error "Migration failed"
                print_info "You can run it later: python database/migrate.py"
            fi
        else
            print_warning "Skipping migration"
            print_info "Run later: python database/migrate.py"
        fi
    else
        print_warning "No data files found"
        print_info "You'll need to add data files to data/ directory"
    fi
fi

echo ""
echo "=========================================="
echo "Step 7: Model Files"
echo "=========================================="

if [ -f "ai_model.pt" ]; then
    MODEL_SIZE=$(du -h ai_model.pt | cut -f1)
    print_success "AI model found (${MODEL_SIZE})"
else
    print_warning "AI model not found (ai_model.pt)"
    print_info "The system will work with reduced accuracy"
fi

echo ""
echo "=========================================="
echo "Step 8: Running Tests"
echo "=========================================="

read -p "Run tests to verify installation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running tests..."
    if pytest tests/ -v --tb=short; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed (this may be normal if data is not migrated)"
    fi
fi

echo ""
echo "=========================================="
echo "Installation Summary"
echo "=========================================="

print_success "Python environment: Ready"
print_success "Dependencies: Installed"
print_success "Configuration: Created"
print_success "Directories: Created"

if [ -f "data/matches.db" ]; then
    print_success "Database: Ready"
else
    print_warning "Database: Not migrated"
fi

if [ -f "ai_model.pt" ]; then
    print_success "AI Model: Available"
else
    print_warning "AI Model: Not found"
fi

echo ""
echo "=========================================="
echo "Next Steps"
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
echo "5. Access the application:"
echo "   Frontend: http://localhost:5000"
echo "   API Docs: http://localhost:5000/api/docs"
echo "   Health: http://localhost:5000/api/health"
echo ""

read -p "Start server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "Starting FFPAS server..."
    echo ""
    python start.py
else
    echo ""
    print_success "Setup complete! Run 'python start.py' when ready."
    echo ""
fi
