@echo off
echo 🔍 Checking for bot conflicts...

python scripts/conflict_checker.py
if errorlevel 1 (
    echo ❌ Bot conflict detected!
    echo Please resolve conflicts and try again.
    pause
    exit /b 1
)

echo ✅ No conflicts detected
echo 🚀 Starting BraveBot...

python main.py
pause@echo off
rem 🚀 BraveBot Windows Startup Script
rem ===================================

setlocal enabledelayedexpansion

echo 🤖 BraveBot Windows Startup
echo ============================

rem Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

rem Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

rem Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

rem Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

rem Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

rem Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo ⚠️ .env file not found. Creating from template...
        copy .env.example .env
        echo ❌ Please edit .env file with your configuration!
        echo Press any key to open the file...
        pause
        notepad .env
        echo Please run this script again after setting up .env
        pause
        exit /b 1
    ) else (
        echo ❌ .env file not found and no template available!
        pause
        exit /b 1
    )
)

rem Initialize database
echo 🗃️ Initializing database...
python -c "from core.database_manager import init_db; init_db(); print('✅ Database ready')"

rem Parse command line arguments
set "RUN_TESTS=false"
set "START_MONITOR=false"
set "START_BACKUP=false"

:parse_args
if "%1"=="--test" (
    set "RUN_TESTS=true"
    shift
    goto parse_args
)
if "%1"=="--monitor" (
    set "START_MONITOR=true"
    shift
    goto parse_args
)
if "%1"=="--backup" (
    set "START_BACKUP=true"
    shift
    goto parse_args
)
if "%1"=="--all" (
    set "RUN_TESTS=true"
    set "START_MONITOR=true"
    set "START_BACKUP=true"
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo.
    echo Options:
    echo   --test      Run tests before starting
    echo   --monitor   Start health monitoring
    echo   --backup    Start backup service
    echo   --all       Enable all features
    echo   --help      Show this help message
    echo.
    pause
    exit /b 0
)

rem Run tests if requested
if "%RUN_TESTS%"=="true" (
    echo 🧪 Running tests...
    python -m pytest tests/ -v --tb=short
    if errorlevel 1 (
        echo ❌ Tests failed!
        pause
        exit /b 1
    )
    echo ✅ All tests passed
)

rem Start monitoring if requested
if "%START_MONITOR%"=="true" (
    echo 🏥 Starting health monitor...
    start "BraveBot Monitor" python scripts/health_monitor.py
)

rem Start backup service if requested
if "%START_BACKUP%"=="true" (
    echo 💾 Starting backup service...
    start "BraveBot Backup" python scripts/backup_system.py
)

rem Start main bot
echo 🚀 Starting BraveBot...
echo Press Ctrl+C to stop
echo ========================

python main.py

echo.
echo 🛑 Bot stopped
pause
