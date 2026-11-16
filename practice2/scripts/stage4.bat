@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === load order: diamond ===
py src\main.py configs\test_simple.xml --load-order
echo.
echo === load order: cycle ===
py src\main.py configs\test_cycle.xml --load-order
echo.
echo === load order: complex graph ===
py src\main.py configs\test_complex.xml --load-order
echo.
echo === load order: chalk ===
py src\main.py configs\chalk.xml --load-order
echo.
