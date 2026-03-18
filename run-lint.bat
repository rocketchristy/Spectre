@echo off
REM Linting Runner
REM Runs ESLint and code quality checks on Frontend

echo.
echo ====================================
echo Frontend Linting
echo ====================================
echo.

cd Frontend
npm run lint

pause
