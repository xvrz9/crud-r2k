@echo off
cd /d "%~dp0"
echo Instalando CRUD R2K. Esto se hace una sola vez y necesita internet.
python --version >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python. Instalelo desde python.org y marque "Add python.exe to PATH".
    pause
    exit /b 1
)
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Hubo un error al instalar. Revise el internet y vuelva a intentarlo.
    pause
    exit /b 1
)
echo.
echo Instalacion terminada. Para abrir la aplicacion use iniciar.bat
pause
