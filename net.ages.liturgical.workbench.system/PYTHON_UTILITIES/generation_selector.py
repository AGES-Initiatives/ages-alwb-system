import tkinter as tk
from tkinter import ttk, messagebox
import os

# --- CONFIGURATION ---
ATEM_FILE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\c-generator-settings\generator.atem"

class GenerationSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Generation Selector")
        self.root.geometry("800x850")
        
        # Data Setup
        self.months_data = [
            ("January", "01"), ("February", "02"), ("March", "03"), ("April", "04"),
            ("May", "05"), ("June", "06"), ("July", "07"), ("August", "08"),
            ("September", "09"), ("October", "10"), ("November", "11"), ("December", "12")
        ]
        self.status_options = ["Final", "Review", "Draft", "NA"]
        
        self.regex_presets = {
            "HTML generation": r"se.m{m}.d{d}.(..|...)",
            "PDF Generation": r"se.m{m}.d{d}.(..|(?!(ma2|h91))\\w{{3}})",
            "Seminary Chapel": r"se.hc.m{m}.d{d}.(ma8)"
        }

        # Variables
        self.month_vars = {m[1]: tk.BooleanVar() for m in self.months_data}
        self.day_vars = {f"{d:02d}": tk.BooleanVar() for d in range(1, 32)}
        self.manual_var = tk.StringVar()

        # Trace changes for real-time sync
        for var in self.month_vars.values():
            var.trace_add("write", self.sync_manual_box)
        for var in self.day_vars.values():
            var.trace_add("write", self.sync_manual_box)

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # --- MONTH SELECTION ---
        m_frame = ttk.LabelFrame(main_frame, text=" 1. Months ", padding="10")
        m_frame.pack(fill="x", pady=(0, 10))
        
        m_header = ttk.Frame(m_frame)
        m_header.pack(fill="x")
        ttk.Label(m_header, text="Select Months:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        ttk.Button(m_header, text="Clear", command=self.clear_all_months, width=8).pack(side="right")
        ttk.Button(m_header, text="Select All", command=self.select_all_months, width=10).pack(side="right", padx=5)

        m_grid = ttk.Frame(m_frame); m_grid.pack(pady=5)
        for i, (name, code) in enumerate(self.months_data):
            ttk.Checkbutton(m_grid, text=name, variable=self.month_vars[code]).grid(row=i//4, column=i%4, sticky="w", padx=10, pady=2)

        # --- DAY SELECTION (GRID) ---
        d_frame = ttk.LabelFrame(main_frame, text=" 2. Days ", padding="10")
        d_frame.pack(fill="x", pady=10)

        d_header = ttk.Frame(d_frame)
        d_header.pack(fill="x")
        ttk.Label(d_header, text="Select Days:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        ttk.Button(d_header, text="Clear", command=self.clear_all_days, width=8).pack(side="right")
        ttk.Button(d_header, text="Select All", command=self.select_all_days, width=10).pack(side="right", padx=5)

        d_grid = ttk.Frame(d_frame); d_grid.pack(pady=5)
        for d in range(1, 32):
            code = f"{d:02d}"
            ttk.Checkbutton(d_grid, text=code, variable=self.day_vars[code], width=4).grid(row=(d-1)//7, column=(d-1)%7, padx=5, pady=2)

        # --- SETTINGS ---
        config_frame = ttk.LabelFrame(main_frame, text=" 3. Settings ", padding="10")
        config_frame.pack(fill="x", pady=5)
        
        ttk.Label(config_frame, text="Preset:").grid(row=0, column=0, sticky="w")
        self.pattern_combo = ttk.Combobox(config_frame, values=list(self.regex_presets.keys()), state="readonly", width=30)
        self.pattern_combo.grid(row=0, column=1, padx=10, sticky="w"); self.pattern_combo.set("HTML generation")
        self.pattern_combo.bind("<<ComboboxSelected>>", self.sync_manual_box)

        ttk.Label(config_frame, text="Status:").grid(row=1, column=0, sticky="w", pady=5)
        self.status_combo = ttk.Combobox(config_frame, values=self.status_options, state="readonly", width=30)
        self.status_combo.grid(row=1, column=1, padx=10, pady=5, sticky="w"); self.status_combo.set("Final")

        # --- FINAL REGEX STAGING AREA ---
        manual_frame = ttk.LabelFrame(main_frame, text=" 4. Final Regex (Review or Edit) ", padding="10")
        manual_frame.pack(fill="x", pady=10)
        
        entry_bar = ttk.Frame(manual_frame)
        entry_bar.pack(fill="x")
        self.manual_entry = ttk.Entry(entry_bar, textvariable=self.manual_var, font=('Consolas', 10))
        self.manual_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(entry_bar, text="Revert", command=self.sync_manual_box, width=8).pack(side="right")

        # --- ACTION ---
        self.btn_save = ttk.Button(main_frame, text="UPDATE GENERATOR (.atem)", command=self.update_file)
        self.btn_save.pack(fill="x", ipady=10, pady=10)

        # Initialize
        self.sync_manual_box()

    def sync_manual_box(self, *args):
        sel_months = sorted([code for code, var in self.month_vars.items() if var.get()])
        sel_days = sorted([code for code, var in self.day_vars.items() if var.get()])
        
        m_part = self.build_regex_group(sel_months, 12)
        d_part = self.build_regex_group(sel_days, 31)
        
        template = self.regex_presets[self.pattern_combo.get()]
        formatted_regex = template.format(m=m_part, d=d_part)
        self.manual_var.set(formatted_regex)

    def build_regex_group(self, selected_items, max_count):
        if len(selected_items) == max_count or len(selected_items) == 0: return "(..)"
        if len(selected_items) == 1: return f"({selected_items[0]})"
        return f"({'|'.join(selected_items)})"

    def select_all_months(self):
        for var in self.month_vars.values(): var.set(True)
    def clear_all_months(self):
        for var in self.month_vars.values(): var.set(False)
    
    def select_all_days(self):
        for var in self.day_vars.values(): var.set(True)
    def clear_all_days(self):
        for var in self.day_vars.values(): var.set(False)

    def update_file(self):
        try:
            final_regex = self.manual_var.get().strip()
            new_regex_line = f'\t\tService_Regular_Expression "{final_regex}.atem"'
            new_status_line = f'\t\tService_Status {self.status_combo.get()}'

            if not os.path.exists(ATEM_FILE):
                messagebox.showerror("Error", f"File not found: {ATEM_FILE}"); return

            with open(ATEM_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
            with open(ATEM_FILE, 'w', encoding='utf-8', newline='') as f:
                for line in lines:
                    if "Service_Regular_Expression" in line: f.write(f"{new_regex_line}\n")
                    elif "Service_Status" in line: f.write(f"{new_status_line}\n")
                    else: f.write(line)
            
            messagebox.showinfo("Success", f"ATEM Updated!\nRegex: {final_regex}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk(); app = GenerationSelector(root); root.mainloop()