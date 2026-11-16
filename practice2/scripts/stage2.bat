@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === express 4.18.2 ===
py src\main.py configs\express.xml
echo.
echo === chalk 4.1.2 ===
py src\main.py configs\chalk.xml
echo.
echo === axios 1.6.0 ===
py src\main.py configs\axios.xml
echo.
