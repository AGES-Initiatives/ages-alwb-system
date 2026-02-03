import os

def check_template():
    # Path to your CLEAN backup (the one without the music list)
    target = r"C:\git\ages-alwb-assets\net.ages.liturgical.workbench.website.assets.ages\root\booksindex.htmlbak"
    
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("TEMPLATE INTEGRITY CHECK (Pre-Injection)")
    print("-" * 40)
    for tag in ['ul', 'li', 'span']:
        op = content.count(f'<{tag}')
        cl = content.count(f'</{tag}>')
        status = "[OK]" if op == cl else "[PRE-EXISTING ERROR]"
        print(f"<{tag:<5}: Opens: {op:<6} | Closes: {cl:<6} | {status}")

if __name__ == "__main__":
    check_template()