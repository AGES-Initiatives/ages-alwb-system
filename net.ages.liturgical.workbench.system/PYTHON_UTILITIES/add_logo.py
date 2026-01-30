import fitz  # PyMuPDF
import os
import re

# --- PATH CONFIGURATION ---
UTILS_DIR = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\PYTHON_UTILITIES"
CONTEXT_FILE = os.path.join(UTILS_DIR, "client_context.txt")
CLIENTS_BASE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\b-preferences"
SRC_GEN_BASE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\src-gen\website"

# 1. Dynamically determine the active client
active_client = "goarch" 
if os.path.exists(CONTEXT_FILE):
    with open(CONTEXT_FILE, 'r') as f:
        active_client = f.read().strip().lower()

def get_website_folder_name(client):
    """Looks into the client's .ares file to find the website folder (e.g., 'goa')"""
    target_ares = f"pref.website_{client}.ares"
    for root_dir, _, files in os.walk(CLIENTS_BASE):
        if target_ares in files:
            path = os.path.join(root_dir, target_ares)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    match = re.search(r'generated\.website\.folder\.root\s*=\s*"([^/]+)/dcs"', content)
                    if match:
                        return match.group(1)
            except:
                pass
    return client

# 2. Point to the dynamic data folder based on the Website setting
web_folder = get_website_folder_name(active_client)
# Constructs: .../src-gen/website/goa/dcs/p/s
data_dir = os.path.join(SRC_GEN_BASE, web_folder, "dcs", "p", "s") 

# 3. Point to exactly where your logo is stored
logo_path = os.path.join(UTILS_DIR, "logo.png")

# --- BRANDING SETTINGS ---
LOGO_SIZE = 1.96 * 72 
BRAND_TAG = "BrandedByPython"
VERTICAL_OFFSET = 126

TARGET_PARENTS = {"co", "co7", "em", "ma", "ma3", "ma4", "ma5", "ma6", "ma9", "pl1", "ve", "ve2", "ve3", "ve4", "ve5", "ve6", "ve9", "vl", "vl2"}
TARGET_SUBS = {"en", "gr", "gr-en"}

success_count = 0
skipped_count = 0
error_count = 0

print("-" * 30)
print(f"ACTIVE CLIENT:  {active_client.upper()}")
print(f"WEBSITE FOLDER: {web_folder}")
print(f"TARGET PATH:    {data_dir}")
print("-" * 30)

if not os.path.exists(data_dir):
    print(f"CRITICAL ERROR: Directory not found: {data_dir}")
    print("Ensure you have run the Eclipse generation for this client.")
    exit()

for root, dirs, files in os.walk(data_dir):
    current_path_lower = root.lower()
    current_folder_name = os.path.basename(current_path_lower)
    path_parts = set(os.path.normpath(current_path_lower).split(os.sep))
    
    if current_folder_name in TARGET_SUBS and path_parts.intersection(TARGET_PARENTS):
        for filename in files:
            if filename.lower().endswith(".pdf") and not filename.startswith("temp_"):
                file_path = os.path.join(root, filename)
                temp_path = os.path.join(root, "temp_" + filename)
                
                try:
                    doc = fitz.open(file_path)
                    metadata = doc.metadata
                    keywords = metadata.get("keywords", "") if metadata.get("keywords") else ""
                    
                    if BRAND_TAG in keywords:
                        skipped_count += 1
                        doc.close()
                        continue
                    
                    page = doc[0]
                    page_w, page_h = page.rect.width, page.rect.height
                    
                    x1 = (page_w - LOGO_SIZE) / 2
                    x2 = x1 + LOGO_SIZE
                    y1 = ((page_h - LOGO_SIZE) / 2) + VERTICAL_OFFSET
                    y2 = y1 + LOGO_SIZE
                    
                    logo_rect = fitz.Rect(x1, y1, x2, y2)
                    page.insert_image(logo_rect, filename=logo_path)
                    
                    new_metadata = metadata.copy()
                    new_metadata["keywords"] = f"{keywords}, {BRAND_TAG}" if keywords else BRAND_TAG
                    doc.set_metadata(new_metadata)
                    
                    doc.save(temp_path)
                    doc.close()
                    
                    os.remove(file_path)
                    os.rename(temp_path, file_path)
                    
                    print(f"[SUCCESS] {filename}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"[ERROR]   {filename}: {e}")
                    error_count += 1
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

print("\n" + "=" * 30)
print(f"FINAL REPORT")
print(f"Branded: {success_count} | Skipped: {skipped_count} | Errors: {error_count}")
print("=" * 30)