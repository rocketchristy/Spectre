@echo off
REM Backend Test Runner
REM Runs Backend tests with pytest

echo.
echo ====================================
echo Backend Tests with pytest
echo ====================================
echo.

REM Get the directory where this batch file is located
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%Backend"

REM Install dependencies
echo Installing dependencies...
"%SCRIPT_DIR%venv\Scripts\python.exe" -m pip install --upgrade -r requirements.txt

REM Run tests using venv python
echo.
echo Running tests...
"%SCRIPT_DIR%venv\Scripts\python.exe" -m pytest tests -v --tb=short

pause
