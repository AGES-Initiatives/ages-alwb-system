import os
import re

def tabs(n):
    return "    " * n # Standard 4-space tabs

def replace_day(arr, d):
    # Matches "mc." + day id to find the liturgical name
    pattern = re.compile(rf"^mc\.{re.escape(d)}.*")
    for line in arr:
        if pattern.match(line):
            try:
                return line[11:].strip().strip('"')
            except:
                continue
    return d

def replace_service(arr, s, tr):
    pattern = re.compile(re.escape(s.lower()) + r"\.html\.link.*")
    for line in arr:
        if pattern.match(line):
            try:
                return line.split('"')[1] + tr
            except:
                continue
    return s

def replace_key(arr, str_val, id_val):
    pattern = re.compile(rf"^pe{id_val}.*\.{str_val}\..*")
    for line in arr:
        if pattern.match(line):
            if ":" in line:
                parts = line.split(":")
                return parts[-1].strip().strip('"')
            else:
                try:
                    return line.split('"')[1]
                except:
                    continue
    return str_val

def main():
    # Paths - Keeping original
    media_map_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/media-maps/media_en_redirects_goarch.ares"
    key_desc_path = "C:/git/alwb-library-en-us-goadedes/alwb.library_en_US_goadedes/Properties/key.descriptors_en_US_goadedes.ares"
    index_desc_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/b-preferences/goarch/website.index.titles_en_US_goarch.ares"
    output_path = "C:/git/ages-alwb-system/net.ages.liturgical.workbench.system/MEDIA_INDEX_UTILITY/output/enPE.html"

    fs = ""
    current_line = [""] * 4 
    previous_line = [""] * 4
    arr_or_singer = ""
    special_tr = "" 
    alt_text = ""
    first_line = True

    # 1. Load Descriptors (Header/Footer logic removed)
    with open(key_desc_path, 'r', encoding='utf-8') as f:
        key_desc = [line.strip() for line in f]
    with open(index_desc_path, 'r', encoding='utf-8') as f:
        day_desc = [line.strip() for line in f]

    # 2. Process Media Map
    with open(media_map_path, 'r', encoding='utf-8') as mm:
        for line in mm:
            str_line = line.strip()
            if not str_line.startswith("pe"):
                continue
            
            str_line = str_line.replace(".MM.", ".")
            
            # Alt Text Logic
            alt_text = ""
            if ".alt1" in str_line:
                str_line = str_line[:8] + str_line[13:]
                alt_text = "Alternative: "
            elif ".alt2" in str_line or ".alt3" in str_line:
                str_line = str_line[:8] + str_line[13:]
                alt_text = "Another Alt.: "

            # Arranger/Singer extraction with slash cleanup
            if "arranger" in str_line or "singer" in str_line:
                try:
                    val = str_line.split('= "')[1].rstrip('"')
                    arr_or_singer = val.strip().rstrip('/')
                except: continue
                continue

            # Substring Extraction
            try:
                current_line[0] = "Pentecostarion"
                day_id = str_line[3:7] 
                service_id = str_line[10:12] 
                dot_after_hymn = str_line.find(".", 13)
                hymn_name = str_line[13:dot_after_hymn]

                # Transformations
                current_line[1] = replace_day(day_desc, day_id)
                current_line[2] = alt_text + replace_service(day_desc, service_id, special_tr)
                current_line[3] = replace_key(key_desc, hymn_name, special_tr + service_id)
            except: continue

            music_style = ""
            if ".w." in str_line: music_style = "Score: Staff"
            elif ".b." in str_line: music_style = "Score: Byzantine"
            elif ".a" in str_line: music_style = "Audio"

            file_name = ""
            for ext in [".pdf", ".mp3", ".m4a"]: # Added m4a for safety
                if ext in str_line:
                    start = str_line.find(".path") + 9
                    end = str_line.find(ext) + len(ext)
                    file_name = str_line[start:end]
                    break

            # --- Snippet Tree Logic ---
            if first_line:
                first_line = False
                for i, val in enumerate(current_line):
                    fs += tabs(i + 1) + f'<li class="level_{i+2}">{val}\n'
                    fs += tabs(i + 2) + "<ul>\n"
                
                fs += tabs(5) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
                previous_line = list(current_line)
                continue

            # Comparison for nesting
            for i in range(len(current_line)):
                if current_line[i] != previous_line[i]:
                    # Close older levels
                    for j in range(len(current_line)-1, i-1, -1):
                        fs += tabs(j + 2) + "</ul>\n"
                        fs += tabs(j + 1) + "</li>\n"
                    # Open new levels
                    for j in range(i, len(current_line)):
                        fs += tabs(j + 1) + f'<li class="level_{j+2}">{current_line[j]}\n'
                        fs += tabs(j + 2) + "<ul>\n"
                    break
            
            fs += tabs(5) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
            previous_line = list(current_line)

    # 3. Final Closers - specifically closing all 4 levels
    for i in range(len(current_line) - 1, -1, -1):
        fs += tabs(i + 2) + "</ul>\n"
        fs += tabs(i + 1) + "</li>\n"

    # 4. Write Snippet
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(fs)
    print("Successfully generated enPE.html snippet.")

if __name__ == "__main__":
    main()