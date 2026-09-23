@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo     AI Financial Assistant - Setup Script
echo ===================================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)
echo [OK] Python is installed.
echo.

echo [2/5] Creating virtual environment (.venv)...
if not exist .venv (
    python -m venv .venv
    echo [OK] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)
echo.

echo [3/5] Activating virtual environment and installing dependencies...
call .venv\Scripts\activate
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check requirements.txt.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.
echo.

echo [4/5] Creating data directory...
if not exist data (
    mkdir data
    echo [OK] Data directory created.
) else (
    echo [INFO] Data directory already exists.
)
echo.

echo [5/5] Running seed_data.py to populate database...
if exist backend\seed_data.py (
    python -m backend.seed_data
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to run seed_data.py.
    ) else (
        echo [OK] Database populated successfully.
    )
) else (
    echo [WARN] backend\seed_data.py not found. Skipping database seeding.
)
echo.

echo ===================================================
echo                  Setup Complete!
echo ===================================================
echo.
echo Next steps:
echo 1. Run 'run.bat' to start the application.
echo.
pause
