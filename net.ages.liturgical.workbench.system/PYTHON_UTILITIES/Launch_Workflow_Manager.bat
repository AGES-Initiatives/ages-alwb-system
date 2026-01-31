@echo off
:: The /d switch handles drive changes, the quotes handle spaces in paths
cd /d "C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\PYTHON_UTILITIES"

:: Check if the file exists before trying to run it
if exist "alwb_workflow_manager.py" (
    start "" pythonw.exe "alwb_workflow_manager.py"
) else (
    echo Error: Dashboard script not found in PYTHON_UTILITIES.
    pause
)
exit