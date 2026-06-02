@echo off
REM Klik-dua-kali untuk menjalankan detektor huruf via kamera.
title SIBI-Bridge - Kamera
cd /d "%~dp0vision"
".venv\Scripts\python.exe" sibi_camera.py
echo.
echo (Jendela ditutup? Tekan tombol apa saja.)
pause >nul
