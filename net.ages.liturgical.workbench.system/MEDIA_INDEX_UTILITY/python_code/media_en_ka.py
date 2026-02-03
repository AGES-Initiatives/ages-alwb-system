import os

def tabs(n):
    return "    " * n # Using 4 spaces per tab for standard HTML indentation

def main():
    # Paths - Keeping your original paths
    media_map_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/media-maps/media_en_redirects_goarch.ares"
    output_path = "C:/git/ages-alwb-system/net.ages.liturgical.workbench.system/MEDIA_INDEX_UTILITY/output/enKA.html"

    fs = ""
    current_line = ["", ""]
    previous_line = ["", ""]
    arr_or_singer = ""
    first_line = True

    # Process Media Map
    with open(media_map_path, 'r', encoding='utf-8') as mm:
        for line in mm:
            str_line = line.strip()
            
            # Filter for Katavasias
            if len(str_line) < 10 or not str_line.startswith("he.k.ka.MM"):
                continue

            # Handle Alt Text logic
            alt_text = ""
            if ".alt1" in str_line:
                str_line = str_line[:11] + str_line[16:]
                alt_text = "Alternative Commemoration: "
            elif ".alt2" in str_line or ".alt3" in str_line:
                str_line = str_line[:11] + str_line[16:]
                alt_text = "Another Alt. Commemoration: "

            # Store Arranger/Singer and strip trailing slashes
            if "arranger" in str_line or "singer" in str_line:
                try:
                    start_idx = str_line.find('= "') + 3
                    end_idx = str_line.rfind('"')
                    arr_or_singer = str_line[start_idx:end_idx].strip().rstrip('/')
                except:
                    continue
                continue

            # Extract Name and Ode
            try:
                ode_idx = str_line.find("Ode")
                dot_after_ode = str_line.find(".", ode_idx)
                name_part = str_line[11:ode_idx]
                ode_part = str_line[ode_idx+3 : dot_after_ode]
            except:
                continue

            # Ode 9 Exception logic
            if ode_part == "9":
                ode_part = "1345678"
                arr_or_singer = "Ode 9"
                if ".a" not in str_line: 
                    continue

            if ode_part != "1345678":
                continue

            # Setup current state: Level 2 = Katavasias, Level 3 = The Canon Name
            current_line = ["Katavasias", name_part]
            
            # Determine Music Style
            music_style = ""
            if ".w." in str_line: music_style = "Score: Staff"
            elif ".b." in str_line: music_style = "Score: Byzantine"
            elif ".a" in str_line: music_style = "Audio"

            # Extract File Path
            file_name = ""
            for ext in [".pdf", ".mp3", ".m4a"]:
                if ext in str_line:
                    path_start = str_line.find(".path") + 9
                    path_end = str_line.find(ext) + len(ext)
                    file_name = str_line[path_start:path_end]
                    break

            # --- HTML Tree Logic ---
            if first_line:
                first_line = False
                # Start at Level 2 (Katavasias)
                fs += tabs(1) + f'<li class="level_2">{current_line[0]}\n'
                fs += tabs(2) + "<ul>\n"
                # Sub-level (The Canon Name)
                fs += tabs(3) + f'<li class="level_3">{current_line[1]}\n'
                fs += tabs(4) + "<ul>\n"
                
                # Leaf Node
                fs += tabs(5) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
                previous_line = list(current_line)
                continue

            # If the Canon name changes, close the previous sub-list and open a new one
            if current_line[1] != previous_line[1]:
                fs += tabs(4) + "</ul>\n"
                fs += tabs(3) + "</li>\n"
                fs += tabs(3) + f'<li class="level_3">{current_line[1]}\n'
                fs += tabs(4) + "<ul>\n"
            
            # Add the leaf node (links)
            fs += tabs(5) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
            previous_line = list(current_line)

    # 3. Final Closing Tags (Closing Level 3 and then Level 2)
    fs += tabs(4) + "</ul>\n"
    fs += tabs(3) + "</li>\n"
    fs += tabs(2) + "</ul>\n"
    fs += tabs(1) + "</li>\n"

    # 4. Write Output
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out:
            out.write(fs)
        print("Successfully generated enKA.html snippet.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()