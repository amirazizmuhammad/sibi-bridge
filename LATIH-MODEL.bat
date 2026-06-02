@echo off
REM Klik-dua-kali untuk melatih model dari dataset yang sudah direkam.
title SIBI-Bridge - Latih Model
cd /d "%~dp0vision"
".venv\Scripts\python.exe" latih_model.py
echo.
pause
