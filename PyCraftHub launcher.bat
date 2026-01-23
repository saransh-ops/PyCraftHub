@echo off
title PyCraftHub

:: -----------------------------
:: CHECK PYTHON
:: -----------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Download Python from https://www.python.org
    pause
    exit
)

:: -----------------------------
:: FIRST-TIME SETUP CHECK
:: -----------------------------
if exist .setup_done goto RUN_APP

echo 🔧 First-time setup detected...
echo 📦 Installing dependencies...

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit
)

echo ✔ Setup completed
echo done > .setup_done

:: -----------------------------
:: RUN PYCRAFTHUB
:: -----------------------------
:RUN_APP
echo 🚀 Launching PyCraftHub...
python main.py
pause
