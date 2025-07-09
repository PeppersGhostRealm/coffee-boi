@echo off
rem ──── move into the script’s folder ────
cd /d "%~dp0"

rem ──── start pythonw (no console) and immediately exit this batch ────
start "" pythonw "%~dp0run_scheduler.py"

exit
