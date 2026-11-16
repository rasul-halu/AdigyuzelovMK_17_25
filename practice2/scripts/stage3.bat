@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === diamond without cycles ===
py src\main.py configs\test_simple.xml
echo.
echo === package without dependencies ===
py src\main.py configs\test_leaf.xml
echo.
echo === cycle A-B-C-A ===
py src\main.py configs\test_cycle.xml
echo.
echo === two cycles B-D and E-E ===
py src\main.py configs\test_complex.xml
echo.
echo === max_depth=2 on chain A-F ===
py src\main.py configs\test_deep2.xml
echo.
echo === real package express, depth 3 ===
py src\main.py configs\express.xml
echo.
