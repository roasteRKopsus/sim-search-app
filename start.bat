@echo off
title M2m tools - RUNNING
color 0B
echo.
echo  ================================================
echo  M2m tools - STARTING...
echo  ================================================
echo.

:: Activate venv
if not exist ".venv" (
    echo [ERROR] .venv not found! Run 1-INSTALL.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

:: Start server + open browser
echo  Starting server at http://127.0.0.1:5000
echo  Login: admin / admin123
echo.
start "" http://127.0.0.1:5000
python run.py

pause