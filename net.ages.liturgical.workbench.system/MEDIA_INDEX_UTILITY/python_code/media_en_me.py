import os
import re

def tabs(n):
    return "    " * n

def replace_month(s):
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    try:
        month_num = int(s[1:])
        return months.get(month_num, "Month")
    except:
        return "Month"

def replace_day(d, m):
    if re.match(r".\d\d", d):
        return f"{m[:3]} {int(d[1:])}"
    else:
        specials = {
            ("dHF", "July"): "Jul 13-19: Sunday of the Holy Fathers",
            ("dHF", "October"): "Oct 11-17: Sunday of the Holy Fathers",
            ("dFF", ""): "Dec 11-17: Sunday of the Forefathers",
            ("dBC", ""): "Dec 18-24: Sunday Before Christmas",
            ("dAC", ""): "Sunday After Christmas"
        }
        return specials.get((d, m), specials.get((d, ""), m))

def replace_service(arr, s):
    pattern = re.compile(re.escape(s.lower()) + r"\.html\.link.*")
    for line in arr:
        if pattern.match(line):
            try:
                return line.split('"')[1]
            except:
                continue
    return s

def replace_key(arr, str_val, service_id):
    pattern = re.compile(rf"^me{service_id}.*\.{str_val}\..*")
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
    # Paths - keeping your original paths
    media_map_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/media-maps/media_en_redirects_goarch.ares"
    key_desc_path = "C:/git/alwb-library-en-us-goadedes/alwb.library_en_US_goadedes/Properties/key.descriptors_en_US_goadedes.ares"
    index_desc_path = "C:/git/ages-alwb-templates/net.ages.liturgical.workbench.templates/b-preferences/goarch/website.index.titles_en_US_goarch.ares"
    output_path = "C:/git/ages-alwb-system/net.ages.liturgical.workbench.system/MEDIA_INDEX_UTILITY/output/enME.html"

    fs = ""
    current_line = [""] * 5
    previous_line = [""] * 5
    arr_or_singer = ""
    first_line = True

    # 1. Load Descriptors (No more header/footer)
    with open(key_desc_path, 'r', encoding='utf-8') as f:
        key_desc = [line.strip() for line in f]
    with open(index_desc_path, 'r', encoding='utf-8') as f:
        day_desc = [line.strip() for line in f]

    # 2. Process Media Map
    with open(media_map_path, 'r', encoding='utf-8') as mm:
        for line in mm:
            str_line = line.strip()
            if not str_line.startswith("me"):
                continue
            
            str_line = str_line.replace(".MM.", ".")
            
            # Alt Text
            alt_text = ""
            if ".alt1" in str_line:
                str_line = str_line[:11] + str_line[16:]
                alt_text = "Alternative Commemoration: "
            elif ".alt2" in str_line or ".alt3" in str_line:
                str_line = str_line[:11] + str_line[16:]
                alt_text = "Another Alt. Commemoration: "

            # Contributor Cleanup
            if "arranger" in str_line or "singer" in str_line:
                try:
                    val = str_line.split('= "')[1].rstrip('"')
                    arr_or_singer = val.strip().rstrip('/') # Clean slashes here
                except:
                    continue
                continue

            # Level Extraction
            try:
                current_line[0] = "Menaion"
                month_code = str_line[3:6]
                day_code = str_line[7:10]
                service_id = str_line[13:15]
                dot_after_name = str_line.find(".", 16)
                media_name = str_line[16:dot_after_name]

                current_line[1] = replace_month(month_code)
                current_line[2] = replace_day(day_code, current_line[1])
                current_line[3] = alt_text + replace_service(day_desc, service_id)
                current_line[4] = replace_key(key_desc, media_name, service_id)
            except:
                continue

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

            # Check for changes in hierarchy
            for i in range(len(current_line)):
                if current_line[i] != previous_line[i]:
                    # Close the changed levels and their children
                    for j in range(len(current_line)-1, i-1, -1):
                        fs += tabs(j + 2) + "</ul>\n"
                        fs += tabs(j + 1) + "</li>\n"
                    # Open the new levels
                    for j in range(i, len(current_line)):
                        fs += tabs(j + 1) + f'<li class="level_{j+2}">{current_line[j]}\n'
                        fs += tabs(j + 2) + "<ul>\n"
                    break
            
            fs += tabs(6) + f'<li dcslink="https://dcs.goarch.org{file_name}">{music_style}<span class="contributor">{arr_or_singer}</span></li>\n'
            previous_line = list(current_line)

    # 3. Final Closers - specifically closing all 5 levels
    for i in range(len(current_line) - 1, -1, -1):
        fs += tabs(i + 2) + "</ul>\n"
        fs += tabs(i + 1) + "</li>\n"

    # 4. Write Snippet
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(fs)
    print("Successfully generated enME.html snippet.")

if __name__ == "__main__":
    main()