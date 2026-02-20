@echo off
:: 1. Navigate to the utility folder
cd /d "%~dp0PYTHON_UTILITIES"

:: 2. Clean up temporary Python cache files to keep the USB clean
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: 3. Launch the dashboard silently using pythonw
start "" pythonw "alwb_workflow_manager.py"

:: 4. Close the batch window
exit