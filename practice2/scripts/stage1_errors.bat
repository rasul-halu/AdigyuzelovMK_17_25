@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo === config.xml (correct) ===
py src\main.py config.xml
echo.
echo === missing config file ===
py src\main.py configs\errors\no_such_file.xml
echo.
echo === bad_ascii_tree ===
py src\main.py configs\errors\bad_ascii_tree.xml
echo.
echo === bad_npm_name ===
py src\main.py configs\errors\bad_npm_name.xml
echo.
echo === bad_output_ext ===
py src\main.py configs\errors\bad_output_ext.xml
echo.
echo === bad_test_mode ===
py src\main.py configs\errors\bad_test_mode.xml
echo.
echo === bad_test_name ===
py src\main.py configs\errors\bad_test_name.xml
echo.
echo === bad_url ===
py src\main.py configs\errors\bad_url.xml
echo.
echo === bad_version ===
py src\main.py configs\errors\bad_version.xml
echo.
echo === broken_xml ===
py src\main.py configs\errors\broken_xml.xml
echo.
echo === depth_not_int ===
py src\main.py configs\errors\depth_not_int.xml
echo.
echo === depth_zero ===
py src\main.py configs\errors\depth_zero.xml
echo.
echo === duplicate_param ===
py src\main.py configs\errors\duplicate_param.xml
echo.
echo === empty_package ===
py src\main.py configs\errors\empty_package.xml
echo.
echo === missing_output_dir ===
py src\main.py configs\errors\missing_output_dir.xml
echo.
echo === missing_param ===
py src\main.py configs\errors\missing_param.xml
echo.
echo === missing_repo_file ===
py src\main.py configs\errors\missing_repo_file.xml
echo.
echo === unknown_param ===
py src\main.py configs\errors\unknown_param.xml
echo.
echo === wrong_root ===
py src\main.py configs\errors\wrong_root.xml
echo.
