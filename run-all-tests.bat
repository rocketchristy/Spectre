@echo off
REM All Tests Runner
REM Runs both Frontend and Backend tests

echo.
echo ====================================
echo Running ALL Tests
echo ====================================
echo.

echo.
echo [1/2] Frontend Tests...
echo ====================================
cd Frontend
call npm run test:unit
if %errorlevel% neq 0 (
    echo Frontend tests failed!
    cd ..
    goto :error
)
cd ..

echo.
echo [2/2] Backend Tests...
echo ====================================
cd Backend
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
call pytest tests -v --tb=short
if %errorlevel% neq 0 (
    echo Backend tests failed!
    cd ..
    goto :error
)
cd ..

echo.
echo ====================================
echo ALL TESTS PASSED!
echo ====================================
echo.
pause
exit /b 0

:error
echo.
echo ====================================
echo TESTS FAILED - See output above
echo ====================================
echo.
pause
exit /b 1
