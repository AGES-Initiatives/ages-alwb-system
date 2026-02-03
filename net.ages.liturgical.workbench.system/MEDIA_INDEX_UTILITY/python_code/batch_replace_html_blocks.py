import os
import re
import shutil

def main():
    # Paths - Using your standard project locations
    target_file = r"C:\git\ages-alwb-assets\net.ages.liturgical.workbench.website.assets.ages\root\booksindex.html"
    output_dir = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\MEDIA_INDEX_UTILITY\output"
    
    # We now target the two main DIV containers
    targets = [
        ("music_list_english", "master_english.html"),
        ("music_list_greek", "master_greek.html")
    ]

    if not os.path.exists(target_file):
        print(f"Error: Target file not found at {target_file}")
        return

    # --- Single Backup Logic (No program association conflict) ---
    backup_path = target_file + "bak"
    try:
        shutil.copy2(target_file, backup_path)
        print(f"Backup created: {os.path.basename(backup_path)}")
    except Exception as e:
        print(f"Warning: Could not create backup. {e}")

    # Read the current master file
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    for div_id, source_file in targets:
        source_path = os.path.join(output_dir, source_file)
        
        if not os.path.exists(source_path):
            print(f"Skipping: {source_file} not found in output directory.")
            continue

        with open(source_path, 'r', encoding='utf-8') as f:
            new_inner_html = f.read().strip()

        # REGEX EXPLANATION:
        # (<div id="ID">) -> Group 1: The opening div tag
        # (.*?)           -> Group 2: Everything currently inside (non-greedy)
        # (</div>)        -> Group 3: The closing div tag
        # flags=re.DOTALL -> Essential: allows the "." to match newlines
        pattern = rf'(<div id="{div_id}">)(.*?)(</div>)'
        
        if re.search(pattern, content, flags=re.DOTALL):
            # We replace the entire match with: Group 1 + New Content + Group 3
            content = re.sub(pattern, rf'\1\n{new_inner_html}\n\3', content, flags=re.DOTALL)
            print(f"Successfully updated container: {div_id}")
        else:
            print(f"Error: Could not find <div id='{div_id}'> in booksindex.html")

    # Write the clean, updated content back to the master file
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n[DONE] booksindex.html updated successfully via Container Overwrite.")

if __name__ == "__main__":
    main()