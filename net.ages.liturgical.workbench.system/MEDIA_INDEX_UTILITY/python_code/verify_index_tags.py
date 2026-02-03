import os

def verify_html(file_path):
    filename = os.path.basename(file_path)
    
    # Apply baselines ONLY to the main website index file
    is_main_index = (filename == "booksindex.html")
    
    BASELINES = {
        'ul': 0,
        'li': 5 if is_main_index else 0,
        'span': -1 if is_main_index else 0
    }

    if not os.path.exists(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Checking HTML integrity: {filename}")
    print("-" * 50)
    
    all_clear = True
    for tag in ['ul', 'li', 'span']:
        opens = content.count(f'<{tag}')
        closes = content.count(f'</{tag}>')
        diff = opens - closes
        expected_diff = BASELINES.get(tag, 0)
        
        if diff == expected_diff:
            status = "[OK]"
        else:
            status = f"[ERROR: Diff {diff}]"
            all_clear = False
            
        print(f"<{tag:<5} / </{tag}> | Opens: {opens:<7} | Closes: {closes:<7} | {status}")

    print("-" * 50)
    if all_clear:
        if is_main_index:
            print("RESULT: INTEGRITY VERIFIED (Matches Template Baseline)")
        else:
            print("RESULT: No tag imbalances detected. Snippet is perfect.")
    else:
        print("RESULT: NEW TAG IMBALANCE DETECTED!")
    
    print("=" * 50)

if __name__ == "__main__":
    target = r"C:\git\ages-alwb-assets\net.ages.liturgical.workbench.website.assets.ages\root\booksindex.html"
    verify_html(target)