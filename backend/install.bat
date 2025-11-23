@echo off
REM Automated installation script for Windows
REM Pie Global Furniture Backend Setup

echo ============================================================
echo  Pie Global Furniture Backend Installation (Windows)
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Step 1: Upgrade pip, setuptools, and wheel
echo ============================================================
echo Step 1: Upgrading pip, setuptools, and wheel...
echo ============================================================
python -m pip install --upgrade pip setuptools>=65.0.0 wheel>=0.38.0
if errorlevel 1 (
    echo ERROR: Failed to upgrade build tools
    pause
    exit /b 1
)
echo.

REM Step 2: Install dependencies
echo ============================================================
echo Step 2: Installing project dependencies...
echo ============================================================
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)
echo.

echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env and configure your settings
echo   2. Run: python manage.py migrate
echo   3. Run: python manage.py createsuperuser
echo   4. Run: python manage.py runserver
echo.
pause
