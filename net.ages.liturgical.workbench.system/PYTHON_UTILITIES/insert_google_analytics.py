import os
import re

# --- PATH CONFIGURATION ---
from path_settings import CONTEXT_FILE, CLIENTS_BASE, SRC_GEN_BASE

# 1. Get active client from context file
active_client = "goarch"
if os.path.exists(CONTEXT_FILE):
    with open(CONTEXT_FILE, 'r') as f:
        active_client = f.read().strip().lower()

def get_website_folder_name(client):
    """Looks into the client's .ares file to find the custom website folder name (e.g., 'goa')"""
    target_ares = f"pref.website_{client}.ares"
    for root_dir, _, files in os.walk(CLIENTS_BASE):
        if target_ares in files:
            path = os.path.join(root_dir, target_ares)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for: generated.website.folder.root = "goa/dcs"
                    match = re.search(r'generated\.website\.folder\.root\s*=\s*"([^/]+)/dcs"', content)
                    if match:
                        return match.group(1)
            except:
                pass
    return client # Fallback to client name if not found

# 2. Dynamically determine the folder name (will return 'goa' instead of 'goarch')
web_folder = get_website_folder_name(active_client)
data_dir = os.path.join(SRC_GEN_BASE, web_folder)

# 3. The Analytics Code
GA_CODE = """<script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXX-Y"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'UA-XXXXX-Y');
</script>
"""

def insert_analytics():
    print(f"Targeting Client: {active_client.upper()}")
    print(f"Website Name from settings: {web_folder}")
    print(f"Searching for HTML in: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"ERROR: Folder not found at {data_dir}")
        print("Check if you have run the Eclipse generator for this client.")
        return

    count = 0
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "www.googletagmanager.com" not in content:
                        # Insert before closing head tag
                        new_content = content.replace("</head>", f"{GA_CODE}\n</head>")
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        count += 1
                except Exception as e:
                    print(f"Could not process {file}: {e}")

    print(f"SUCCESS: Analytics inserted into {count} files.")

if __name__ == "__main__":
    insert_analytics()