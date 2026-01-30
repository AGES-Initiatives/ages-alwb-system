import sys
import os
import re

# --- SHARED PATHS ---
UTILS_DIR = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\PYTHON_UTILITIES"
CONTEXT_FILE = os.path.join(UTILS_DIR, "client_context.txt")
CLIENTS_BASE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\b-preferences"

def toggle_indexer():
    if len(sys.argv) < 2:
        return

    new_state = sys.argv[1].lower() # "yes" or "no"
    
    try:
        with open(CONTEXT_FILE, 'r') as f:
            client = f.read().strip()
    except:
        print("Error: Could not read client_context.txt")
        return

    # Dynamic filename based on active client
    filename = "pref.website_" + client + ".ares"
    target_path = os.path.join(CLIENTS_BASE, client, filename)

    if not os.path.exists(target_path):
        print("File Not Found: " + filename)
        return

    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Target the specific key: generate.services.index
        pattern = r'(generate\.services\.index\s*=\s*")([^"]+)(")'
        if re.search(pattern, content):
            new_content = re.sub(pattern, rf'\1{new_state}\3', content)
            
            with open(target_path, 'w', encoding='utf-8', newline='') as f:
                f.write(new_content)
            
            print("SUCCESS: " + client + " Indexer set to " + ("ON" if new_state == "yes" else "OFF"))
        else:
            print("ERROR: Key 'generate.services.index' not found in " + filename)

    except Exception as e:
        print("IO Error: " + str(e))

if __name__ == "__main__":
    toggle_indexer()