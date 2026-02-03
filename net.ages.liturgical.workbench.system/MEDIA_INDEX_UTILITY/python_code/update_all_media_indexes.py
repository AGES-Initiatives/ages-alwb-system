import os

def run_all():
    output_dir = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\MEDIA_INDEX_UTILITY\output"
    
    # Map the master files to the individual snippet files they should contain
    groups = {
        "master_english.html": ["enKA.html", "enME.html", "enOC.html", "enPE.html", "enTR.html"],
        "master_greek.html": ["grKA.html", "grME.html", "grOC.html", "grPE.html", "grTR.html"]
    }

    print("=" * 60)
    print("   AGES Liturgical Workbench: File-Based Master Stitcher")
    print("=" * 60)

    for master_filename, snippets in groups.items():
        lang_label = "English" if "english" in master_filename else "Greek"
        tree_id = "dcs_tree_01" if "english" in master_filename else "dcs_tree_02"
        
        # Start the Master Block
        master_content = f'<ul id="{tree_id}">\n'
        master_content += f'  <li class="level_1">Music List ({lang_label})\n    <ul>\n'
        
        for snippet in snippets:
            snippet_path = os.path.join(output_dir, snippet)
            if os.path.exists(snippet_path):
                print(f"Stitching: {snippet:<15}", end=" ", flush=True)
                with open(snippet_path, 'r', encoding='utf-8') as f:
                    # Append the actual file content
                    master_content += f.read() + "\n"
                print("[OK]")
            else:
                print(f"MISSING: {snippet}")

        # Close the tags
        master_content += "    </ul>\n  </li>\n</ul>"
        
        # Write the Master File
        with open(os.path.join(output_dir, master_filename), 'w', encoding='utf-8') as f:
            f.write(master_content)
            
        print(f"COMPLETED: {master_filename} ({len(master_content)} characters)")
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_all()