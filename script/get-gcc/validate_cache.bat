@echo off
setlocal enabledelayedexpansion

:: Check if MLC_GCC_DIR_PATH is defined and exists
if not defined MLC_GCC_DIR_PATH (
    goto end
)
if not exist "%MLC_GCC_DIR_PATH%" (
    goto end
)

:: Resolve absolute paths using PowerShell
for /f "delims=" %%A in ('powershell -NoProfile -Command "(Resolve-Path -LiteralPath \"%MLC_GCC_DIR_PATH%\").Path"') do set "resolvedPath1=%%A"
for /f "delims=" %%B in ('powershell -NoProfile -Command "(Resolve-Path -LiteralPath \"%MLC_GCC_INSTALLED_PATH%\").Path"') do set "resolvedPath2=%%B"

:: Compare the resolved paths (case-insensitive on Windows)
if /i not "!resolvedPath1!"=="!resolvedPath2!" (
    exit /b 1
)

:end
exit /b 0

