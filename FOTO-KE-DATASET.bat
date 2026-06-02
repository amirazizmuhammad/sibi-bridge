@echo off
REM Klik-dua-kali: ubah foto di folder vision\foto (subfolder per huruf) jadi dataset.
REM Susunan: vision\foto\A\ (foto huruf A), vision\foto\B\, dst.
title SIBI-Bridge - Foto ke Dataset
cd /d "%~dp0vision"
".venv\Scripts\python.exe" dataset_dari_foto.py
echo.
pause
