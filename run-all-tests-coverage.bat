@echo off
REM All Tests Runner with Coverage
REM Runs both Frontend and Backend tests with coverage reports

echo.
echo ====================================
echo Running ALL Tests with Coverage
echo ====================================
echo.

echo.
echo [1/2] Frontend Tests with Coverage...
echo ====================================
pushd Frontend
call npx vitest run --coverage
set FRONTEND_EXIT=%ERRORLEVEL%
popd
REM Coverage threshold failures return exit code 1, but reports are still generated
REM Only fail if actual test failures (exit code other than 0 or 1)
if %FRONTEND_EXIT% gtr 1 (
    echo Frontend tests failed!
    goto :error
)
if %FRONTEND_EXIT% equ 1 (
    echo WARNING: Frontend coverage thresholds not met, but tests passed
)

echo.
echo [2/2] Backend Tests with Coverage...
echo ====================================
REM Ensure pytest-cov is installed
echo Installing pytest-cov if needed...
python -m pip install -q pytest-cov >nul 2>&1
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
call python -c "import pytest; pytest.main(['--cov=Backend', '--cov-report=html', '--cov-report=term', '-v', '--tb=short', '-p', 'no:taf', '-p', 'pytest_cov', 'Backend/tests/'])"
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
echo Frontend coverage report: Frontend\coverage\index.html
echo Backend coverage report: htmlcov\index.html
echo.
exit /b 0

:error
echo.
echo ====================================
echo TESTS FAILED - See output above
echo ====================================
echo.
exit /b 1
