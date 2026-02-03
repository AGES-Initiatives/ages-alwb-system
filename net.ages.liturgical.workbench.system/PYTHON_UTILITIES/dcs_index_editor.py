import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

class DcsIndexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("DCS Website Index Editor - Python Dashboard")
        self.root.geometry("850x750")

        # Configuration: The constant base path
        self.base_path = Path(r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\src-gen\website")
        
        self.current_file = None
        self.service_rows = []

        # --- Header Section ---
        header = ttk.Frame(self.root, padding="10")
        header.pack(fill=tk.X)

        # 1. Website Discovery
        ttk.Label(header, text="Website:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.site_var = tk.StringVar()
        sites = self.discover_websites()
        self.site_combo = ttk.Combobox(header, textvariable=self.site_var, values=sites, state="readonly")
        self.site_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        if "goa" in sites: self.site_combo.set("goa")

        # 2. Date Selection
        date_frame = ttk.Frame(header)
        date_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        
        self.year_var = tk.StringVar(value="2026")
        self.month_var = tk.StringVar(value="01")
        self.day_var = tk.StringVar(value="01")

        years = [str(y) for y in range(2024, 2035)]
        months = [f"{m:02d}" for m in range(1, 13)]
        days = [f"{d:02d}" for d in range(1, 32)]

        ttk.Combobox(date_frame, textvariable=self.year_var, values=years, width=6).pack(side=tk.LEFT)
        ttk.Label(date_frame, text="/").pack(side=tk.LEFT)
        ttk.Combobox(date_frame, textvariable=self.month_var, values=months, width=4).pack(side=tk.LEFT)
        ttk.Label(date_frame, text="/").pack(side=tk.LEFT)
        ttk.Combobox(date_frame, textvariable=self.day_var, values=days, width=4).pack(side=tk.LEFT)

        # 3. Action Buttons
        btn_frame = ttk.Frame(header)
        btn_frame.grid(row=1, column=2, padx=20)
        
        ttk.Button(btn_frame, text="Load File", command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save All", command=self.save_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="View in Browser", command=self.open_browser).pack(side=tk.LEFT, padx=2)

        # 4. Status Label
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground="blue", font=("Courier", 9))
        self.status_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # --- Main Editor Area (Scrollable) ---
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def discover_websites(self):
        try:
            return sorted([d.name for d in self.base_path.iterdir() if d.is_dir()])
        except:
            return ["Error: Path not found"]

    def load_file(self):
        filename = f"{self.year_var.get()}{self.month_var.get()}{self.day_var.get()}.html"
        self.current_file = self.base_path / self.site_var.get() / "dcs" / "indexes" / filename

        if not self.current_file.exists():
            messagebox.showerror("Error", f"File not found:\n{self.current_file}")
            self.status_var.set(f"Status: ERROR - {filename} missing")
            return

        self.status_var.set(f"Editing: {self.current_file}")
        self.refresh_editor()

    def refresh_editor(self):
        # Clear previous rows
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.service_rows = []

        content = self.current_file.read_text(encoding="utf-8")
        # Regex to find the spans
        pattern = r"<span class='index-service-day'>(.*?)</span>"
        matches = re.finditer(pattern, content)

        for match in matches:
            original_text = match.group(1)
            row_frame = ttk.Frame(self.scroll_frame, padding=5)
            row_frame.pack(fill=tk.X)
            
            ttk.Label(row_frame, text="Service:").pack(side=tk.LEFT)
            entry = ttk.Entry(row_frame, width=80)
            entry.insert(0, original_text)
            entry.pack(side=tk.LEFT, padx=10)
            
            self.service_rows.append({'original': original_text, 'entry': entry})

    def save_changes(self):
        if not self.current_file: return
        
        content = self.current_file.read_text(encoding="utf-8")
        for row in self.service_rows:
            old = row['original']
            new = row['entry'].get()
            # Escaping for safety
            content = content.replace(f"class='index-service-day'>{old}</span>", 
                                      f"class='index-service-day'>{new}</span>")

        self.current_file.write_text(content, encoding="utf-8")
        messagebox.showinfo("Success", "File updated successfully!")
        self.refresh_editor()

    def open_browser(self):
        if self.current_file:
            os.startfile(self.current_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = DcsIndexEditor(root)
    root.mainloop()