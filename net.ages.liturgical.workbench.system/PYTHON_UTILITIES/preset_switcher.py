import os
import re
import sys

# --- CONFIGURATION PATHS ---
# Using raw strings to avoid escape sequence warnings
TARGET_FILE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\c-generator-settings\pref.generation_alwb.ares"
ATEM_DIRECTORY = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\a-templates\Pdf_Covers"

def update_settings(settings):
    """Reads the .ares file and updates keys while strictly preserving indentation."""
    if not os.path.exists(TARGET_FILE):
        print(f"CRITICAL ERROR: File not found: {TARGET_FILE}")
        return

    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        processed_line = line
        for key, value in settings.items():
            # regex explanation: 
            # group 1: (^[\t ]*) captures leading tabs/spaces
            # group 2: ({re.escape(key)}\s*=\s*) captures the key and equals sign
            # group 3: ([^\s/]+|\"[^\"]*\") captures the existing value
            pattern = rf"(^[\t ]*)({re.escape(key)}\s*=\s*)([^\s/]+|\"[^\"]*\")"
            match = re.search(pattern, processed_line)
            
            if match:
                indent = match.group(1)
                key_part = match.group(2)
                old_val = match.group(3)
                
                # Maintain quotes if they were there originally
                new_val = f'"{value}"' if old_val.startswith('"') else value
                processed_line = f"{indent}{key_part}{new_val}\n"
                break # Move to next line once a key is matched
        
        new_lines.append(processed_line)

    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        f.flush()
        os.fsync(f.fileno()) # Force SSD to commit changes immediately

def handle_atem_updates(mode):
    """Scans .atem files and flips Switch-Version lines."""
    if mode in ["PDF_E", "PDF_GE"]:
        search, target = "Switch-Version L1 End-Switch-Version", "Switch-Version L2 End-Switch-Version"
    else:
        search, target = "Switch-Version L2 End-Switch-Version", "Switch-Version L1 End-Switch-Version"

    count = 0
    for root, _, files in os.walk(ATEM_DIRECTORY):
        for file in files:
            if file.endswith(".atem"):
                path = os.path.join(root, file)
                if update_single_atem(path, search, target):
                    count += 1
                    # Fixed path reporting for cleaner logs
                    print(f"   [Flipped] {file}")
    return count

def update_single_atem(path, search, target):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    for line in lines:
        if "Both" in line:
            new_lines.append(line)
        elif line.strip() == search:
            # Replaces the content while keeping newline characters
            new_lines.append(line.replace(search, target))
            modified = True
        else:
            new_lines.append(line)
            
    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            f.flush()
            os.fsync(f.fileno())
    return modified

def main():
    if len(sys.argv) < 2:
        print("Usage: preset_switcher.py [MODE]")
        return
    
    mode = sys.argv[1].upper()
    settings = {}

    # --- HTML LOGIC ---
    if mode.startswith("HTML"):
        settings.update({"generate.file.html": "yes", "generate.file.pdf": "no"})
        if mode == "HTML_GE_E":
            settings.update({
                "generate.file.html.version.v1": "no", 
                "generate.file.html.version.v2": "yes", 
                "generate.file.html.version.v1v2": "yes"
            })
        else:
            settings["generate.file.html.version.v1"] = "yes" if mode == "HTML_G" else "no"
            settings["generate.file.html.version.v2"] = "yes" if mode == "HTML_E" else "no"
            settings["generate.file.html.version.v1v2"] = "yes" if mode == "HTML_GE" else "no"
            
    # --- PDF LOGIC ---
    elif mode.startswith("PDF"):
        settings.update({"generate.file.html": "no", "generate.file.pdf": "yes"})
        settings["generate.file.pdf.version.v1"] = "yes" if mode == "PDF_G" else "no"
        settings["generate.file.pdf.version.v2"] = "yes" if mode == "PDF_E" else "no"
        settings["generate.file.pdf.version.v1v2"] = "yes" if mode == "PDF_GE" else "no"
        
        if mode == "PDF_GE":
            settings.update({
                "cover.version": "pdf.covers_en_US_goarch.GE.text", 
                "page.columns.quantity": "1", 
                "page.columns.gap": "0in"
            })
        else:
            lang = "G" if mode == "PDF_G" else "E"
            settings.update({
                "cover.version": f"pdf.covers_en_US_goarch.{lang}.text", 
                "page.columns.quantity": "2", 
                "page.columns.gap": ".1in"
            })
        
        print(f"Scanning .atem files in: {ATEM_DIRECTORY}")
        count = handle_atem_updates(mode)
        print(f">>> ATEM Update: {count} files updated.")

    update_settings(settings)
    print("-" * 46 + f"\nSUCCESS: Mode [{mode}] applied.\n" + "-" * 46)

if __name__ == "__main__":
    main()