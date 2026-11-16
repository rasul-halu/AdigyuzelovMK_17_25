@echo off
rem Сравнение с настоящим npm: npm ls --all для пакета.
rem Использование: scripts\compare_npm.bat <пакет> <версия>   (нужен Node.js)
chcp 65001 >nul
cd /d "%~dp0.."
set PKG=%1
set VER=%2
if "%PKG%"=="" set PKG=chalk
if "%VER%"=="" set VER=4.1.2
set OUT=%CD%\output
set TMPDIR=%TEMP%\npm_compare_%RANDOM%
mkdir "%TMPDIR%"
pushd "%TMPDIR%"
call npm init -y >nul
call npm install %PKG%@%VER% --ignore-scripts --no-audit --no-fund >nul
call npm ls --all > "%OUT%\npm_ls_%PKG%.txt"
popd
rmdir /s /q "%TMPDIR%"
type "%OUT%\npm_ls_%PKG%.txt"
