@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Primero ejecute instalar.bat
    pause
    exit /b 1
)
set PYTHONPATH=%~dp0src
.venv\Scripts\python -m r2k.app
pause
