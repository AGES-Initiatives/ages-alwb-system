import subprocess
import pyautogui
import pygetwindow as gw
import time
import os

# --- PRECISE CONFIGURATION ---
# Identifier for your Oxygen02 workspace window
WORKSPACE_IDENTIFIER = r"C:\ALWB_WORKSPACES\Workspace-git-Oxygen02"

# The exact path to the Eclipse executable (Oxygen.2)
ECLIPSE_EXE = r"C:\Users\AGES user\eclipse\java-oxygen2\eclipse\eclipse.exe"

# The exact path to your generator file in the git templates folder
GENERATOR_FILE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\c-generator-settings\generator.atem"

def run_generator_macro():
    """
    Triggers the generation function by ensuring generator.atem is active in Oxygen.2.
    """
    try:
        # 1. Identify the Eclipse Window
        all_titles = gw.getAllTitles()
        target_title = next((t for t in all_titles if WORKSPACE_IDENTIFIER in t), None)
        
        if not target_title:
            return False, "Error: Eclipse Oxygen.2 window not found. Is the workspace open?"
        
        win = gw.getWindowsWithTitle(target_title)[0]

        # 2. Check if the specific generator file is the active tab
        # We look for the filename in the window title
        if "generator.atem" not in win.title.lower():
            if os.path.exists(GENERATOR_FILE):
                # Pass the file path to eclipse.exe to open it in the active session
                subprocess.Popen([ECLIPSE_EXE, GENERATOR_FILE])
                # Oxygen.2 (running on jre1.8.0_471) requires time to load the DSL editor
                time.sleep(4.0) 
            else:
                return False, f"Error: File not found: {GENERATOR_FILE}"

        # 3. Bring Oxygen.2 to the foreground
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(1.0) 

        # 4. Click in the Editor (Safety Step)
        # Ensures focus is inside the code editor and not on a side-pane
        center_x = win.left + (win.width // 2)
        center_y = win.top + (win.height // 2)
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)

        # 5. Trigger the Ctrl+G function
        pyautogui.hotkey('ctrl', 'g')
        
        return True, "Success: Ctrl+G triggered for generator.atem"

    except Exception as e:
        return False, f"Automation Error: {str(e)}"

if __name__ == "__main__":
    success, message = run_generator_macro()
    print(message)