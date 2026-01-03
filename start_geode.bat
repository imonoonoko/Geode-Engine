@echo off
chcp 65001 > nul
title Geode-Engine Core
echo ==========================================
echo   Geode-Engine - Brain Stem Startup
echo ==========================================
echo.
echo Starting Python Backend...
set PYTHONPATH=%cd%
REM Set your API key in .env file or uncomment below:
REM set GEMINI_API_KEY=your_api_key_here
python src/brain_stem/main.py
echo.
echo Geode-Engine has stopped.
pause
