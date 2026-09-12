@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python download_youtube.py %*
pause