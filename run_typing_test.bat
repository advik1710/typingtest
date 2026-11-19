@echo off
cd /d "%~dp0"
py typing_test.py
if errorlevel 1 python typing_test.py
pause
