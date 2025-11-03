@echo off
title M2M tools - INSTALLER
color 0A
echo.
echo  ================================================
echo  m2m tools - ONE-CLICK INSTALLER
echo  Created by roasteRKopsus
echo  ================================================
echo.

:: Check admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] Python not found. Installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo [SUCCESS] Python installed. Restart required!
    pause
    exit /b 0
)

:: Create .venv
if not exist ".venv" (
    echo [2/4] Creating virtual environment...
    python -m venv .venv
)

:: Activate & install
call .venv\Scripts\activate.bat
echo [3/4] Installing dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt > install.log 2>&1

:: Create folders
mkdir uploads 2>nul

:: Init DB
echo [4/4] Initializing database...
python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('DB ready')" >nul

echo.
echo  INSTALL COMPLETE!
echo  Now run: 2-START.bat
echo.
pause