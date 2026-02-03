import os
import re

def tabs(n):
    return "    " * n # Standard 4-space indentation

def main():
    # Paths - Keeping original paths for Greek Katavasias
    media_map_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/media-maps/media_en_redirects_goarch.ares"
    output_path = "C:/git/ages-alwb-system/net.ages.liturgical.workbench.system/MEDIA_INDEX_UTILITY/output/grKA.html"

    fs = ""
    current_line = [""] * 2  # 2 levels for Katavasias
    previous_line = [""] * 2
    arr_or_singer = ""
    first_line = True

    # 1. Process Media Map
    with open(media_map_path, 'r', encoding='utf-8') as mm:
        for line in mm:
            str_line = line.strip()
            
            # Filter: he.k.ka.MM
            if len(str_line) < 10 or str_line[:10] != "he.k.ka.MM":
                continue

            # Alt Text Logic
            if ".alt1" in str_line or ".alt2" in str_line or ".alt3" in str_line:
                str_line = str_line[:11] + str_line[16:]

            # Arranger/Singer Logic with slash cleanup
            if "arranger" in str_line or "singer" in str_line:
                try:
                    val = str_line.split('= "')[1].rstrip('"')
                    arr_or_singer = val.strip().rstrip('/')
                except: continue
                continue

            # Ode Logic (Extraction)
            try:
                ode_index = str_line.find("Ode")
                if ode_index == -1: continue
                
                current_line[0] = "Katavasias"
                current_line[1] = str_line[11:ode_index]
                
                # Extract Ode number
                after_ode = str_line[ode_index + 3:]
                dot_index = after_ode.find(".")
                current_line_t = after_ode[:dot_index]

                # Catch Ode 9 - Logic from your Java source
                if current_line_t == "9":
                    current_line_t = "1345678"
                    arr_or_singer = "Ode 9"
                    if ".a" not in str_line: # Only allow audio for Ode 9
                        continue
                
                if current_line_t != "1345678":
                    continue
            except: continue

            # Style and Filename
            music_style = ""
            if ".w." in str_line: music_style = "Score: Staff"
            elif ".b." in str_line: music_style = "Score: Byzantine"
            elif ".a" in str_line: music_style = "Audio"

            file_name = ""
            for ext in [".pdf", ".mp3", ".m4a"]:
                if ext in str_line:
                    start = str_line.find(".path") + 9
                    end = str_line.find(ext) + len(ext)
                    file_name = str_line[start:end]
                    break

            # --- Snippet Nesting Logic ---
            if first_line:
                first_line = False
                for i, val in enumerate(current_line):
                    fs += tabs(i + 1) + f'<li class="level_{i+2}">{val}\n'
                    fs += tabs(i + 2) + "<ul>\n"
                
                fs += tabs(3) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
                previous_line = list(current_line)
                continue

            # Level comparison
            for i in range(len(current_line)):
                if current_line[i] != previous_line[i]:
                    for j in range(len(current_line)-1, i-1, -1):
                        fs += tabs(j + 2) + "</ul>\n"
                        fs += tabs(j + 1) + "</li>\n"
                    for j in range(i, len(current_line)):
                        fs += tabs(j + 1) + f'<li class="level_{j+2}">{current_line[j]}\n'
                        fs += tabs(j + 2) + "<ul>\n"
                    break
            
            fs += tabs(3) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
            previous_line = list(current_line)

    # 3. Final Closers
    for i in range(len(current_line) - 1, -1, -1):
        fs += tabs(i + 2) + "</ul>\n"
        fs += tabs(i + 1) + "</li>\n"

    # 4. Write Snippet
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(fs)
    print("Successfully generated grKA.html snippet.")

if __name__ == "__main__":
    main()