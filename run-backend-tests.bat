@echo off
REM Backend Test Runner
REM Runs Backend tests with pytest

echo.
echo ====================================
echo Backend Tests with pytest
echo ====================================
echo.


REM Activate virtual environment
call venv\Scripts\activate.bat

cd Backend

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Run tests
echo.
echo Running tests...
pytest tests -v --tb=short

pause
