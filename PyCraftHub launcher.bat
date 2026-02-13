@echo off
title PyCraftHub Launcher
color 0B

echo.
echo ========================================
echo     PyCraftHub Launcher
echo ========================================
echo.

REM Check if Python is installed
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed!
    echo.
    echo Download Python from: https://www.python.org
    echo.
    pause
    exit /b 1
)
echo Python found!
echo.

REM Create directories if they don't exist
echo Setting up directories...
if not exist "servers" mkdir servers
if not exist "data" mkdir data
echo Done!
echo.

REM Check if first time setup
if exist .setup_done goto skip_install

echo First time setup - Installing dependencies...
echo.
python -m pip install requests psutil colorama --break-system-packages
echo.

if errorlevel 1 (
    echo.
    echo WARNING: Installation had issues, trying without flag...
    python -m pip install requests psutil colorama
)

echo Setup complete!
echo. > .setup_done
echo.

:skip_install
echo Starting PyCraftHub...
echo.
echo ========================================
echo.

REM Run the main program
python main.py

REM Check if program crashed
if errorlevel 1 (
    color 0C
    echo.
    echo ========================================
    echo ERROR: PyCraftHub crashed!
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Delete .setup_done and run again
    echo 2. Make sure main.py exists
    echo 3. Check error message above
    echo.
)

echo.
pause