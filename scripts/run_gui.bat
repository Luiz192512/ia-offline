@echo off
cd /d "%~dp0\.."
set "PORTABLE_PYTHON=%CD%\portable\python\python.exe"
if exist "%PORTABLE_PYTHON%" (
  "%PORTABLE_PYTHON%" -m app.main --mode gui
) else (
  python -m app.main --mode gui
)
