@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  MindMate - Student Wellness Companion
echo ========================================

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto error
)

echo Installing or checking required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Starting MindMate at http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
goto end

:error
echo.
echo Setup failed. Check the error above and make sure Python 3.10+ is installed.
echo If package installation failed, check your internet connection and try again.
pause
:end
endlocal
