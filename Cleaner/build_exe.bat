@echo off
setlocal
title Build SHIV_Cleaner.exe
cd /d "%~dp0"

:: Needs 64-bit Python 3.9+ from python.org (tick "Add Python to PATH" while installing)
where py >nul 2>&1
if errorlevel 1 (
    echo Python launcher "py" not found. Install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

set "ICON_PI="
set "ICON_NK="
if exist "shiv.ico" (
    set "ICON_PI=--icon shiv.ico"
    set "ICON_NK=--windows-icon-from-ico=shiv.ico"
)

echo.
echo   SHIV Cleaner - EXE builder
echo   ----------------------------------------------------------
echo   [1] PyInstaller   fast and simple
echo   [2] Nuitka        compiles to C: harder to reverse-engineer
echo                     (first run downloads a C compiler, needs internet)
echo.
choice /c 12 /n /m "  Select 1 or 2 : "
if errorlevel 2 goto nuitka

:pyinstaller
py -m pip install --upgrade pip pyinstaller
py -m PyInstaller --onefile --console --uac-admin --clean --noconfirm --name SHIV_Cleaner %ICON_PI% SHIV_Cleaner.py
if errorlevel 1 goto failed
echo.
echo   Done: dist\SHIV_Cleaner.exe
goto end

:nuitka
py -m pip install --upgrade pip nuitka zstandard ordered-set
py -m nuitka --onefile --assume-yes-for-downloads --windows-uac-admin --windows-console-mode=force ^
  --company-name="Shiv Computer" --product-name="SHIV Ultimate System Cleaner" ^
  --file-description="SHIV Ultimate System Cleaner" --file-version=2.0.0.0 --product-version=2.0.0.0 ^
  %ICON_NK% --output-filename=SHIV_Cleaner.exe SHIV_Cleaner.py
if errorlevel 1 goto failed
echo.
echo   Done: SHIV_Cleaner.exe  (in this folder)
goto end

:failed
echo.
echo   Build failed - read the messages above.

:end
pause
