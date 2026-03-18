@echo off
REM Frontend Test Runner
REM Runs Frontend unit tests with Vitest

echo.
echo ====================================
echo Frontend Tests with Vitest
echo ====================================
echo.

cd Frontend
npm run test:unit

pause
