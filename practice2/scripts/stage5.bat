@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === test: diamond ===
py src\main.py configs\test_simple.xml
echo.
echo === test: cycle ===
py src\main.py configs\test_cycle.xml
echo.
echo === test: complex ===
py src\main.py configs\test_complex.xml
echo.
echo === express ===
py src\main.py configs\express.xml
echo.
echo === chalk ===
py src\main.py configs\chalk.xml
echo.
echo === axios ===
py src\main.py configs\axios.xml
echo.
