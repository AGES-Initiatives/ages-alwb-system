import time
import sys
import os

# Import your orchestration and utility modules
try:
    import update_all_media_indexes
    import batch_replace_html_blocks
    import verify_index_tags
except ImportError as e:
    print(f"Error: Missing orchestration scripts. {e}")
    print("Ensure update_all_media_indexes.py, batch_replace_html_blocks.py,")
    print("and verify_index_tags.py are in this folder.")
    sys.exit(1)

def main():
    # Define target for verification
    target_file = r"C:\git\ages-alwb-assets\net.ages.liturgical.workbench.website.assets.ages\root\booksindex.html"
    
    print("=" * 65)
    print("      AGES LITURGICAL WORKBENCH: TOTAL MEDIA REFRESH")
    print("=" * 65)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_total = time.time()

    # --- PHASE 1: GENERATION ---
    # Runs the 10 individual book modules to create HTML snippets
    print("\nPHASE 1: Generating HTML Snippets...")
    print("-" * 65)
    try:
        gen_success = update_all_media_indexes.run_all()
        if not gen_success:
            print("\n[WARNING] Some snippets failed to generate. Check Phase 1 output.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Phase 1 Generation crashed: {e}")
        sys.exit(1)

    # --- PHASE 2: INJECTION ---
    # Grafts the new snippets into the master booksindex.html file
    print("\nPHASE 2: Injecting Snippets into booksindex.html...")
    print("-" * 65)
    try:
        batch_replace_html_blocks.main()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Phase 2 Injection crashed: {e}")
        sys.exit(1)

    # --- PHASE 3: VERIFICATION ---
    # Validates that tag counts (ul, li, span) are balanced
    print("\nPHASE 3: Verifying HTML Integrity...")
    try:
        verify_index_tags.verify_html(target_file)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Phase 3 Verification crashed: {e}")

    end_total = time.time()
    
    print("\n" + "=" * 65)
    print(f"OVERALL UPDATE PROCESS FINISHED")
    print(f"TOTAL ELAPSED TIME: {end_total - start_total:.2f} seconds.")
    print("=" * 65)

if __name__ == "__main__":
    main()
    print("\nDIAGNOSTIC: Checking individual snippets...")
    # This points to your output folder
    output_folder = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\MEDIA_INDEX_UTILITY\output"
    
    for filename in os.listdir(output_folder):
        if filename.endswith(".html"):
            verify_index_tags.verify_html(os.path.join(output_folder, filename))