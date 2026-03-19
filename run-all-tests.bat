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
pushd Frontend
call npm run test:run
set FRONTEND_EXIT=%ERRORLEVEL%
popd
if %FRONTEND_EXIT% neq 0 (
    echo Frontend tests failed!
    goto :error
)

echo.
echo [2/2] Backend Tests...
echo ====================================
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
call python -c "import pytest; pytest.main(['-v', '--tb=short', '-p', 'no:taf', 'Backend/tests/'])"
set BACKEND_EXIT=%ERRORLEVEL%
if %BACKEND_EXIT% neq 0 (
    echo Backend tests failed!
    goto :error
)

echo.
echo ====================================
echo ALL TESTS PASSED!
echo ====================================
echo.
exit /b 0

:error
echo.
echo ====================================
echo TESTS FAILED - See output above
echo ====================================
echo.
exit /b 1
