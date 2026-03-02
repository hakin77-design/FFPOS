@echo off
REM FFPAS Quick Setup Script for Windows
REM Tek komutla tüm kurulumu yapar

setlocal enabledelayedexpansion

color 0B
cls

echo ===============================================================
echo.
echo    ███████╗███████╗██████╗  █████╗ ███████╗
echo    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝
echo    █████╗  █████╗  ██████╔╝███████║███████╗
echo    ██╔══╝  ██╔══╝  ██╔═══╝ ██╔══██║╚════██║
echo    ██║     ██║     ██║     ██║  ██║███████║
echo    ╚═╝     ╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝
echo.
echo    Quick Setup Script v2.0
echo.
echo ===============================================================
echo.

echo This script will:
echo 1. Check system requirements
echo 2. Install Python dependencies
echo 3. Setup environment configuration
echo 4. Create necessary directories
echo 5. Optionally run database migration
echo 6. Start the server
echo.
set /p CONTINUE="Continue? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo Installation cancelled.
    exit /b 0
)

echo.
echo ==========================================
echo Step 1: System Requirements Check
echo ==========================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
) else (
    python --version
    echo [√] Python is installed
)

REM Check pip
echo.
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [!] pip not found, installing...
    python -m ensurepip --upgrade
) else (
    pip --version
    echo [√] pip is installed
)

REM Check Redis (optional)
echo.
echo Checking Redis...
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo [!] Redis not installed (caching will be disabled)
    echo    To install Redis on Windows:
    echo    https://github.com/microsoftarchive/redis/releases
) else (
    echo [√] Redis is installed
)

echo.
echo ==========================================
echo Step 2: Virtual Environment
echo ==========================================
echo.

if exist "venv" (
    echo [i] Virtual environment already exists
    set /p RECREATE="Recreate? (Y/N): "
    if /i "!RECREATE!"=="Y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo [√] Virtual environment recreated
    )
) else (
    echo Creating virtual environment...
    python -m venv venv
    echo [√] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [√] Virtual environment activated

echo.
echo ==========================================
echo Step 3: Installing Dependencies
echo ==========================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip -q

echo Installing requirements (this may take a few minutes)...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [X] Failed to install some dependencies
    echo Try manually: pip install -r requirements.txt
    pause
    exit /b 1
) else (
    echo [√] All dependencies installed
)

echo.
echo ==========================================
echo Step 4: Directory Setup
echo ==========================================
echo.

if not exist "logs" mkdir logs
echo [√] logs\ directory created

if not exist "data" mkdir data
echo [√] data\ directory created

echo.
echo ==========================================
echo Step 5: Environment Configuration
echo ==========================================
echo.

if exist ".env" (
    echo [i] .env file already exists
    set /p OVERWRITE="Overwrite with template? (Y/N): "
    if /i "!OVERWRITE!"=="Y" (
        copy .env.example .env >nul
        echo [√] .env file created from template
    )
) else (
    copy .env.example .env >nul
    echo [√] .env file created from template
)

echo.
echo [!] Please edit .env file with your configuration
echo Required settings:
echo   - API keys (if using external APIs)
echo   - Database URL
echo   - Redis configuration
echo.
set /p EDIT_ENV="Edit .env now? (Y/N): "
if /i "%EDIT_ENV%"=="Y" (
    notepad .env
)

echo.
echo ==========================================
echo Step 6: Database Setup
echo ==========================================
echo.

if exist "data\matches.db" (
    echo [√] Database already exists
    for %%A in ("data\matches.db") do set DB_SIZE=%%~zA
    set /a DB_SIZE_MB=!DB_SIZE! / 1048576
    echo [i] Database size: !DB_SIZE_MB! MB
) else (
    echo [!] No database found
    
    REM Check if JSON files exist
    set JSON_COUNT=0
    for %%F in (data\*.json) do set /a JSON_COUNT+=1
    
    if !JSON_COUNT! GTR 0 (
        echo [i] Found !JSON_COUNT! JSON data files
        set /p RUN_MIGRATION="Run database migration now? (Y/N): "
        if /i "!RUN_MIGRATION!"=="Y" (
            echo [i] Starting migration (this may take 5-10 minutes)...
            python database\migrate.py
            if errorlevel 1 (
                echo [X] Migration failed
                echo You can run it later: python database\migrate.py
            ) else (
                echo [√] Database migration completed
            )
        ) else (
            echo [!] Skipping migration
            echo Run later: python database\migrate.py
        )
    ) else (
        echo [!] No data files found
        echo You'll need to add data files to data\ directory
    )
)

echo.
echo ==========================================
echo Step 7: Model Files
echo ==========================================
echo.

if exist "ai_model.pt" (
    for %%A in ("ai_model.pt") do set MODEL_SIZE=%%~zA
    set /a MODEL_SIZE_MB=!MODEL_SIZE! / 1048576
    echo [√] AI model found (!MODEL_SIZE_MB! MB)
) else (
    echo [!] AI model not found (ai_model.pt)
    echo The system will work with reduced accuracy
)

echo.
echo ==========================================
echo Step 8: Running Tests
echo ==========================================
echo.

set /p RUN_TESTS="Run tests to verify installation? (Y/N): "
if /i "%RUN_TESTS%"=="Y" (
    echo Running tests...
    pytest tests\ -v --tb=short
    if errorlevel 1 (
        echo [!] Some tests failed (this may be normal if data is not migrated)
    ) else (
        echo [√] All tests passed
    )
)

echo.
echo ==========================================
echo Installation Summary
echo ==========================================
echo.

echo [√] Python environment: Ready
echo [√] Dependencies: Installed
echo [√] Configuration: Created
echo [√] Directories: Created

if exist "data\matches.db" (
    echo [√] Database: Ready
) else (
    echo [!] Database: Not migrated
)

if exist "ai_model.pt" (
    echo [√] AI Model: Available
) else (
    echo [!] AI Model: Not found
)

echo.
echo ==========================================
echo Next Steps
echo ==========================================
echo.
echo 1. Review configuration:
echo    notepad .env
echo.
echo 2. If database not migrated:
echo    python database\migrate.py
echo.
echo 3. Start the server:
echo    python start.py
echo.
echo 4. Or use Docker:
echo    docker-compose up -d
echo.
echo 5. Access the application:
echo    Frontend: http://localhost:5000
echo    API Docs: http://localhost:5000/api/docs
echo    Health: http://localhost:5000/api/health
echo.

set /p START_NOW="Start server now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo.
    echo [i] Starting FFPAS server...
    echo.
    python start.py
) else (
    echo.
    echo [√] Setup complete! Run 'python start.py' when ready.
    echo.
    pause
)

endlocal
