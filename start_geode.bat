@echo off
chcp 65001 > nul
title Geode-Engine - Geological Memory AI
echo ==================================================
echo   Geode-Engine - Geological Memory AI
echo   Phase 19: HDC-LLM Bridge Enabled
echo ==================================================
echo.

REM Check Python version
python --version 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check virtual environment
if not exist ".venv" (
    echo [WARN] Virtual environment not found. Creating...
    python -m venv .venv
    echo [INFO] Please activate .venv and run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/3] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check .env file
if not exist ".env" (
    echo [WARN] .env file not found. Creating from template...
    copy .env.example .env
    echo [INFO] Please edit .env and set your GEMINI_API_KEY
    pause
    exit /b 1
)

REM Set Python path
set PYTHONPATH=%cd%

echo [2/3] Checking dependencies...
echo.

REM Optional: Check if Ollama is running (for local LLM)
echo [INFO] Checking Ollama (optional for local LLM)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not detected. Using Gemini API only.
) else (
    echo [OK] Ollama detected!
)

echo.
echo [3/3] Starting Geode-Engine...
echo.
python src/brain_stem/main.py

echo.
echo ==================================================
echo   Geode-Engine has stopped.
echo ==================================================
pause
