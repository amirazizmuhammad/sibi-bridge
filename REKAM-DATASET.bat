@echo off
REM Klik-dua-kali untuk merekam contoh huruf (untuk model akurat).
REM Di jendela kamera: tekan tombol huruf A-Z sambil peragakan, tahan ~2 detik. Q = simpan.
title SIBI-Bridge - Rekam Dataset
cd /d "%~dp0vision"
".venv\Scripts\python.exe" rekam_dataset.py
echo.
pause
