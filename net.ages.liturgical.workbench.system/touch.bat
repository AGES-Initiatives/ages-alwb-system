@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   UNIVERSAL AUTO-DETECT REFRESH
echo ========================================

:: 1. SEARCH LOGIC
if exist "C:\git\alwb-library-gr-us-goa" (
    set "REPO_ROOT=C:\git"
    echo [DETECTED] Local PC Environment (C:\git)
    goto :FOUND
) 

if exist "%~d0\git\alwb-library-gr-us-goa" (
    set "REPO_ROOT=%~d0\git"
    echo [DETECTED] USB Environment (%~d0\git)
    goto :FOUND
) 

if exist "%~d0\alwb-library-gr-us-goa" (
    set "REPO_ROOT=%~d0"
    echo [DETECTED] USB Root Environment (%~d0)
    goto :FOUND
)

:: If it gets here, nothing was found
echo [!] ERROR: Could not locate the library folders.
pause
exit

:FOUND
echo.
:: 2. THE WORK
set "PROJECTS="alwb-library-gr-us-goa" "ages-alwb-library-en-us-goa""
set "TOTAL_TOUCHED=0"

for %%P in (%PROJECTS%) do (
    set "TARGET_DIR=%REPO_ROOT%\%%~P"
    if exist "!TARGET_DIR!" (
        echo [PROCESSING] !TARGET_DIR!
        pushd "!TARGET_DIR!"
        for /r %%f in (*.ares) do (
            copy /b "%%f"+,, "%%f" >nul 2>&1
            set /a TOTAL_TOUCHED+=1
        )
        popd
    )
)

echo.
echo ========================================
echo   SUCCESS: !TOTAL_TOUCHED! files refreshed.
echo ========================================
pause