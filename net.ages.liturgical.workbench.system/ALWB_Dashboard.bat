@echo off
:: Navigate to your dashboard folder
cd /d "C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\PYTHON_UTILITIES"

:: Launch the dashboard using 'pythonw' (this hides the black console window)
start "" pythonw "alwb_workflow_manager.py"

exit