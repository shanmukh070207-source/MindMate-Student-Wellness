@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run run_mindmate_windows.bat first to create the virtual environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m ml.train_model
if errorlevel 1 pause
endlocal
