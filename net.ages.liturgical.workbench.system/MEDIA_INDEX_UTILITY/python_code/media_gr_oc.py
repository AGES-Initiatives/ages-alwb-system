import os
import re

def tabs(n):
    return "    " * n # Standard 4-space indentation

def replace_mode(s):
    return f"Mode {s[1:]}"

def replace_day(d):
    days = {
        "d1": "Sunday", "d2": "Monday", "d3": "Tuesday",
        "d4": "Wednesday", "d5": "Thursday", "d6": "Friday", "d7": "Saturday"
    }
    return days.get(d, d)

def replace_service(arr, s, tr):
    postfix = " (in Triodion)" if tr == "tr" else ""
    pattern = re.compile(re.escape(s.lower()) + r"\.html\.link.*")
    for line in arr:
        if pattern.match(line):
            try:
                return line.split('"')[1] + postfix
            except:
                continue
    return s + postfix

def replace_key(arr, str_val, id_val):
    pattern = re.compile(rf"^oc{id_val}.*\.{str_val}\..*")
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
    # Paths - Keeping original for Greek Octoechos
    media_map_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/media-maps/media_en_redirects_goarch.ares"
    key_desc_path = "C:/git/alwb-library-en-us-goadedes/alwb.library_en_US_goadedes/Properties/key.descriptors_en_US_goadedes.ares"
    index_desc_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/b-preferences/goarch/website.index.titles_en_US_goarch.ares"
    output_path = "C:/git/ages-alwb-system/net.ages.liturgical.workbench.system/MEDIA_INDEX_UTILITY/output/grOC.html"

    fs = ""
    current_line = [""] * 5
    previous_line = [""] * 5
    arr_or_singer = ""
    first_line = True

    # 1. Load External Data
    with open(key_desc_path, 'r', encoding='utf-8') as f:
        key_desc = [line.strip() for line in f]
    with open(index_desc_path, 'r', encoding='utf-8') as f:
        day_desc = [line.strip() for line in f]

    # 2. Process Media Map
    with open(media_map_path, 'r', encoding='utf-8') as mm:
        for line in mm:
            str_line = line.strip()
            
            if not str_line.startswith("oc"):
                continue
            
            str_line = str_line.replace(".MM.", ".")
            
            # Special Triodion Check
            if ".octr" in str_line:
                str_line = str_line.replace(".octr", ".oc")
                special_tr = "tr"
            else:
                special_tr = ""

            # Arranger/Singer extraction with slash cleanup
            if "arranger" in str_line or "singer" in str_line:
                try:
                    val = str_line.split('= "')[1].rstrip('"')
                    arr_or_singer = val.strip().rstrip('/')
                except: continue
                continue

            # Key Parsing
            try:
                current_line[0] = "Octoechos"
                mode_code = str_line[3:5]      # m8
                day_code = str_line[6:8]       # d1
                service_id = str_line[11:13]   # MA
                dot_after_hymn = str_line.find(".", 14)
                hymn_name = str_line[14:dot_after_hymn]

                # Transformations
                current_line[1] = replace_mode(mode_code)
                current_line[2] = replace_day(day_code)
                current_line[3] = replace_service(day_desc, service_id, special_tr)
                current_line[4] = replace_key(key_desc, hymn_name, special_tr + service_id)
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
                
                fs += tabs(6) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
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
            
            fs += tabs(6) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
            previous_line = list(current_line)

    # 3. Final Closers
    for i in range(len(current_line) - 1, -1, -1):
        fs += tabs(i + 2) + "</ul>\n"
        fs += tabs(i + 1) + "</li>\n"

    # 4. Write Snippet
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(fs)
    print("Successfully generated grOC.html snippet.")

if __name__ == "__main__":
    main()