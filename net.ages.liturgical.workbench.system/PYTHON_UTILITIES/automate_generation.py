import subprocess
import pyautogui
import pygetwindow as gw
import time
import os

# --- PRECISE CONFIGURATION ---
from path_settings import WORKSPACE_IDENTIFIER, ECLIPSE_EXE, GENERATOR_FILE

def run_generator_macro():
    """
    Triggers the generation function by ensuring generator.atem is active in Workspace-git-Oxygen02.
    """
    try:
        # 1. Identify the Eclipse Window
        all_titles = gw.getAllTitles()
        
        # Look for the folder name "Workspace-git-Oxygen02" instead of the full C:\ path
        workspace_folder_name = os.path.basename(WORKSPACE_IDENTIFIER)
        
        # Search criteria: Must contain the workspace folder name
        target_title = next((t for t in all_titles if workspace_folder_name in t), None)
        
        # Secondary search: if folder name isn't there, look for "Oxygen"
        if not target_title:
            target_title = next((t for t in all_titles if "Oxygen" in t), None)
        
        if not target_title:
            # If it still fails, we'll list the first few open windows in the error to see what's wrong
            visible_windows = [t for t in all_titles if t.strip()][:5]
            return False, f"Error: Eclipse window not found. (Looking for: {workspace_folder_name}). Visible windows: {visible_windows}"
        
        win = gw.getWindowsWithTitle(target_title)[0]

        # 2. Check if the specific generator file is the active tab
        if "generator.atem" not in win.title.lower():
            if os.path.exists(GENERATOR_FILE):
                # Hardcoded C: drive path to eclipse.exe from path_settings
                subprocess.Popen([ECLIPSE_EXE, GENERATOR_FILE])
                # Wait for Oxygen.2 (JRE 1.8) to load the editor
                time.sleep(4.0) 
            else:
                return False, f"Error: File not found: {GENERATOR_FILE}"

        # 3. Bring Oxygen.2 to the foreground
        if win.isMinimized:
            win.restore()
        
        win.activate()
        time.sleep(1.0) 

        # 4. Click in the Editor (Safety Step)
        center_x = win.left + (win.width // 2)
        center_y = win.top + (win.height // 2)
        pyautogui.click(center_x, center_y)
        time.sleep(0.5)

        # 5. Trigger the Ctrl+G function
        pyautogui.hotkey('ctrl', 'g')
        
        return True, "Success: Ctrl+G triggered for generator.atem"

    except Exception as e:
        return False, f"Automation Error: {str(e)}"

if __name__ == "__main__":
    success, message = run_generator_macro()
    print(message)