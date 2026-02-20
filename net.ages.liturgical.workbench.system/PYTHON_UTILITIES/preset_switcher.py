import os
import re
import sys
import path_settings # Gold Standard Import

def update_settings(settings):
    """Updates the .ares file with strict indentation."""
    if not os.path.exists(path_settings.TARGET_FILE):
        print(f"CRITICAL ERROR: File not found: {path_settings.TARGET_FILE}")
        return

    with open(path_settings.TARGET_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        processed_line = line
        for key, value in settings.items():
            # Matches key = value while preserving leading whitespace
            pattern = rf"(^[\t ]*)({re.escape(key)}\s*=\s*)([^\s/]+|\"[^\"]*\")"
            match = re.search(pattern, processed_line)
            if match:
                indent, key_part, old_val = match.groups()
                # Ensure quotes are maintained if they existed
                new_val = f'"{value}"' if old_val.startswith('"') else value
                processed_line = f"{indent}{key_part}{new_val}\n"
                break 
        new_lines.append(processed_line)

    with open(path_settings.TARGET_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def handle_atem_updates(mode):
    r"""Scans parent and sub-folders (\ma, \ve, \other) for .atem files."""
    if mode == "PDF_G":
        target_lang = "L1"
    elif mode in ["PDF_E", "PDF_GE"]:
        target_lang = "L2"
    else:
        return 0

    # Ensure COVERS_DIR is defined in path_settings.py
    search_path = getattr(path_settings, 'COVERS_DIR', None)
    if not search_path or not os.path.exists(search_path):
        print(f"ERROR: Covers directory not found: {search_path}")
        return 0

    count = 0
    for root, _, files in os.walk(search_path):
        for file in files:
            if file.endswith(".atem"):
                path = os.path.join(root, file)
                if update_single_atem(path, target_lang):
                    count += 1
                    rel_folder = os.path.basename(root)
                    print(f"   [Flipped] ({rel_folder}) {file}")
    return count

def update_single_atem(path, target_lang):
    """Updates Switch-Version lines using regex to handle L1, L2, or L:00 variants."""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    pattern = r"Switch-Version\s+L[12].*?End-Switch-Version"
    replacement = f"Switch-Version {target_lang} End-Switch-Version"

    for line in lines:
        if "Both" in line:
            new_lines.append(line)
        elif "Switch-Version" in line and "End-Switch-Version" in line:
            new_line = re.sub(pattern, replacement, line)
            if new_line != line:
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)
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
        
        lang = "G" if mode == "PDF_G" else "E"
        settings.update({
            "cover.version": f"pdf.covers_en_US_goarch.{lang}.text", 
            "page.columns.quantity": "1" if mode == "PDF_GE" else "2",
            "page.columns.gap": "0in" if mode == "PDF_GE" else ".1in"
        })
        
        print(f"Scanning for covers in: {path_settings.COVERS_DIR}")
        count = handle_atem_updates(mode)
        print(f">>> ATEM Update: {count} files updated.")

    # --- EXECUTION ---
    if settings:
        update_settings(settings)
        print("-" * 46 + f"\nSUCCESS: Mode [{mode}] applied.\n" + "-" * 46)
    else:
        print(f"WARNING: No settings defined for mode [{mode}]. Check logic.")

if __name__ == "__main__":
    main()