import os
import re
import sys

# --- THE BASE PATH ---
from path_settings import BASE_TEMPLATES_DIR

def validate_templates(target_month_code):
    month_path = os.path.join(BASE_TEMPLATES_DIR, target_month_code)
    
    print(f"DEBUG: Searching in: {month_path}")

    if not os.path.exists(month_path):
        print(f"ERROR: The folder '{target_month_code}' does not exist at that location.")
        return

    print(f"--- VALIDATION REPORT FOR {target_month_code.upper()} ---")
    print(f"{'Filename':<20} | {'Status':<10} | {'Set_Date':<12} | {'Match?'}")
    print("-" * 55)

    all_files = []
    # Walk through the month folder and its dXX subfolders
    for root, dirs, files in os.walk(month_path):
        for f in files:
            # We look for files that contain the date pattern .mXX.dXX. 
            # regardless of the final extension (.li, .ares, .html, etc.)
            if re.search(r'\.m\d{2}\.d\d{2}\.', f):
                all_files.append(os.path.join(root, f))
    
    if not all_files:
        print(f"DEBUG: Found 0 files matching the date pattern in {month_path}")
        return

    # Sort by filename to keep days together
    all_files.sort(key=lambda x: os.path.basename(x))

    last_day = None
    month_int = int(target_month_code.replace("m", ""))

    for full_path in all_files:
        filename = os.path.basename(full_path)
        
        # Extract day from filename for grouping and comparison
        day_match = re.search(r'\.d(\d{2})\.', filename)
        current_day_str = day_match.group(1) if day_match else "00"
        file_day_int = int(current_day_str)
        
        # Line break when the day changes
        if last_day is not None and current_day_str != last_day:
            print("-" * 55)
        
        last_day = current_day_str

        set_date_str = "MISSING"
        status_str = "UNKNOWN"
        match_flag = "--"

        try:
            # Open with ignore errors to handle various file encodings
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.readlines()
                
                found_date = False 
                
                for line in content:
                    # 2. Only check if we haven't found the first date yet
                    if "Set_Date" in line and not found_date:
                        m_m = re.search(r'month\s+(\d+)', line)
                        d_m = re.search(r'day\s+(\d+)', line)
                        y_m = re.search(r'year\s+(\d+)', line)
                        
                        if m_m and d_m:
                            s_m, s_d = int(m_m.group(1)), int(d_m.group(1))
                            s_y = y_m.group(1) if y_m else "????"
                            set_date_str = f"{s_y} M:{s_m} D:{s_d}"
                            
                            if s_m == month_int and s_d == file_day_int:
                                match_flag = "OK"
                            else:
                                match_flag = "MISMATCH"
                            
                            # 3. SET THE FLAG TO TRUE so it ignores any later "Set_Date" lines
                            found_date = True 
                    
                    # (Status can keep looking as it's usually unique or consistent)
                    if line.strip().startswith("Status"):
                        status_str = line.replace("Status", "").strip()

            print(f"{filename:<20} | {status_str:<10} | {set_date_str:<12} | {match_flag}")
            
        except Exception as e:
            # If a file is truly unreadable (binary, etc.), we report the error but keep going
            print(f"{filename:<20} | ERROR READING FILE: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        validate_templates(sys.argv[1])
    else:
        print("Error: No month argument provided.")