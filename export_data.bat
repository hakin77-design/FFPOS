@echo off
REM FFPAS Data Export Script for Windows
REM Bu script tüm gerekli dosyaları ve verileri yedekler

setlocal enabledelayedexpansion

echo ==========================================
echo FFPAS Data Export Script
echo ==========================================

REM Tarih damgası
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set EXPORT_DIR=ffpas_export_%TIMESTAMP%
set ARCHIVE_NAME=%EXPORT_DIR%.zip

echo Export directory: %EXPORT_DIR%
echo Archive name: %ARCHIVE_NAME%

REM Export dizinini oluştur
mkdir "%EXPORT_DIR%" 2>nul

echo.
echo 1. Copying application files...
xcopy /E /I /Q ai "%EXPORT_DIR%\ai\" 2>nul
xcopy /E /I /Q api "%EXPORT_DIR%\api\" 2>nul
xcopy /E /I /Q database "%EXPORT_DIR%\database\" 2>nul
xcopy /E /I /Q utils "%EXPORT_DIR%\utils\" 2>nul
xcopy /E /I /Q tests "%EXPORT_DIR%\tests\" 2>nul
xcopy /E /I /Q frontend "%EXPORT_DIR%\frontend\" 2>nul

echo 2. Copying configuration files...
copy config.py "%EXPORT_DIR%\" 2>nul
copy requirements.txt "%EXPORT_DIR%\" 2>nul
copy .env.example "%EXPORT_DIR%\" 2>nul
copy .gitignore "%EXPORT_DIR%\" 2>nul
copy Dockerfile "%EXPORT_DIR%\" 2>nul
copy docker-compose.yml "%EXPORT_DIR%\" 2>nul
copy Makefile "%EXPORT_DIR%\" 2>nul
copy pytest.ini "%EXPORT_DIR%\" 2>nul
copy start.py "%EXPORT_DIR%\" 2>nul

echo 3. Copying documentation...
copy README*.md "%EXPORT_DIR%\" 2>nul
copy ANALIZ_RAPORU.md "%EXPORT_DIR%\" 2>nul
copy UPGRADE_GUIDE.md "%EXPORT_DIR%\" 2>nul

echo 4. Copying data files...
mkdir "%EXPORT_DIR%\data" 2>nul

if exist "data\matches.db" (
    echo    - Copying SQLite database...
    copy data\matches.db "%EXPORT_DIR%\data\" 2>nul
    echo    √ Database copied
) else (
    echo    - No SQLite database found, copying JSON files...
    copy data\*.json "%EXPORT_DIR%\data\" 2>nul
)

if exist "data\teams.json" (
    copy data\teams.json "%EXPORT_DIR%\data\" 2>nul
    echo    √ teams.json copied
)

echo 5. Copying model files...
if exist "ai_model.pt" (
    copy ai_model.pt "%EXPORT_DIR%\" 2>nul
    echo    √ ai_model.pt copied
)

if exist "goals_model.pt" (
    copy goals_model.pt "%EXPORT_DIR%\" 2>nul
    echo    √ goals_model.pt copied
)

echo 6. Creating installation script...
(
echo @echo off
echo REM FFPAS Installation Script for Windows
echo.
echo echo ==========================================
echo echo FFPAS v2.0 Installation
echo echo ==========================================
echo.
echo REM Python version check
echo echo 1. Checking Python version...
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo Error: Python is not installed
echo     pause
echo     exit /b 1
echo ^)
echo python --version
echo.
echo REM Virtual environment
echo echo.
echo echo 2. Creating virtual environment...
echo if not exist "venv" ^(
echo     python -m venv venv
echo     echo    √ Virtual environment created
echo ^) else ^(
echo     echo    √ Virtual environment already exists
echo ^)
echo.
echo REM Activate virtual environment
echo echo.
echo echo 3. Activating virtual environment...
echo call venv\Scripts\activate.bat
echo.
echo REM Install dependencies
echo echo.
echo echo 4. Installing dependencies...
echo python -m pip install --upgrade pip
echo pip install -r requirements.txt
echo echo    √ Dependencies installed
echo.
echo REM Create directories
echo echo.
echo echo 5. Creating directories...
echo if not exist "logs" mkdir logs
echo if not exist "data" mkdir data
echo echo    √ Directories created
echo.
echo REM Environment configuration
echo echo.
echo echo 6. Setting up environment...
echo if not exist ".env" ^(
echo     copy .env.example .env
echo     echo    √ .env file created
echo     echo    ⚠ Please edit .env file with your configuration
echo ^) else ^(
echo     echo    √ .env file already exists
echo ^)
echo.
echo REM Database setup
echo echo.
echo echo 7. Database setup...
echo if exist "data\matches.db" ^(
echo     echo    √ Database already exists
echo ^) else ^(
echo     echo    ⚠ No database found
echo     echo    Run: python database\migrate.py
echo ^)
echo.
echo echo ==========================================
echo echo Installation Complete!
echo echo ==========================================
echo echo.
echo echo Next steps:
echo echo 1. Edit .env file
echo echo 2. If no database: python database\migrate.py
echo echo 3. Start server: python start.py
echo echo.
echo pause
) > "%EXPORT_DIR%\install.bat"

REM INSTALLATION.md oluştur
(
echo # FFPAS v2.0 - Installation Guide
echo.
echo ## Windows Installation
echo.
echo 1. Extract the ZIP file
echo 2. Run install.bat
echo 3. Edit .env file
echo 4. Run: python start.py
echo.
echo ## Requirements
echo - Python 3.10+
echo - 2GB RAM
echo - 1GB disk space
echo.
echo ## Configuration
echo Edit .env file with your settings
echo.
echo ## Database
echo - If matches.db exists: Ready to use
echo - If only JSON files: Run python database\migrate.py
echo.
echo ## Verification
echo curl http://localhost:5000/api/health
echo.
echo ## Documentation
echo See README_V2.md for full documentation
) > "%EXPORT_DIR%\INSTALLATION.md"

echo.
echo 7. Creating ZIP archive...
REM PowerShell ile ZIP oluştur
powershell -command "Compress-Archive -Path '%EXPORT_DIR%' -DestinationPath '%ARCHIVE_NAME%' -Force"

if exist "%ARCHIVE_NAME%" (
    for %%A in ("%ARCHIVE_NAME%") do set ARCHIVE_SIZE=%%~zA
    set /a ARCHIVE_SIZE_MB=!ARCHIVE_SIZE! / 1048576
    
    echo.
    echo ==========================================
    echo Export Complete!
    echo ==========================================
    echo Archive: %ARCHIVE_NAME%
    echo Size: !ARCHIVE_SIZE_MB! MB
    echo.
    echo Contents:
    echo   - Application code
    echo   - Data files
    echo   - Model files
    echo   - Configuration templates
    echo   - Installation script
    echo   - Documentation
    echo.
    echo To install on another PC:
    echo 1. Copy %ARCHIVE_NAME% to target PC
    echo 2. Extract the ZIP file
    echo 3. Run install.bat
    echo.
    echo Cleaning up temporary directory...
    rmdir /s /q "%EXPORT_DIR%"
    echo Done!
) else (
    echo Error: Failed to create archive
    echo Please install 7-Zip or WinRAR and create archive manually
    pause
)

endlocal
