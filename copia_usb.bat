@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src
.venv\Scripts\python -m r2k.copia
pause
