import os
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
import re
import threading

# --- SHARED PATHS ---
UTILS_DIR = r"C:\git\ages-alwb-system\net.ages.liturgical.workbench.system\PYTHON_UTILITIES"
LOGO_ICON_PATH = os.path.join(UTILS_DIR, "logo.png") 

CONTEXT_FILE = os.path.join(UTILS_DIR, "client_context.txt")
PRESET_STATUS = os.path.join(UTILS_DIR, "status_preset.txt")
MASTER_ARES = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\c-generator-settings\pref.master.templates.ares"
CLIENTS_BASE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\b-preferences"

# Worker Scripts
PRESET_SCRIPT = os.path.join(UTILS_DIR, "preset_switcher.py")
LOGO_SCRIPT = os.path.join(UTILS_DIR, "add_logo.py")
ANALYTICS_SCRIPT = os.path.join(UTILS_DIR, "insert_google_analytics.py")
INDEXER_SCRIPT = os.path.join(UTILS_DIR, "toggle_client_indexer.py")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, justify='left', background="#ffffe1", 
                 relief='solid', borderwidth=1, font=("tahoma", "8"), padx=4, pady=2).pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ALWBDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ALWB Dashboard")
        
        # Icon Logic
        try:
            if os.path.exists(LOGO_ICON_PATH):
                self.icon_img = tk.PhotoImage(file=LOGO_ICON_PATH)
                self.root.iconphoto(True, self.icon_img) 
            else:
                self.root.wm_iconbitmap(default='')
        except Exception:
            self.root.wm_iconbitmap(default='')

        self.full_height, self.compact_height = 510, 330 
        self.root.geometry(f"600x{self.full_height}")
        
        # --- RESIZABLE RE-ENABLED ---
        self.root.resizable(True, True) 
        self.root.minsize(580, 330) # Prevent it from getting too squished

        style = ttk.Style()
        style.theme_use('xpnative')
        style.configure('TCombobox', font=('Segoe UI', 9))
        style.configure('TButton', font=('Segoe UI', 9))
        style.configure('Alert.TButton', font=('Segoe UI', 9, 'bold'), foreground="red")
        style.configure('Post.TButton', font=('Segoe UI', 9), anchor="w", padding=(10, 2, 10, 2))

        # --- SYSTEM STATUS ---
        status_frame = ttk.LabelFrame(root, text=" System Status ", padding="10")
        status_frame.pack(fill="x", padx=15, pady=5)
        
        row1 = ttk.Frame(status_frame)
        row1.pack(fill="x", anchor="w")
        ttk.Label(row1, text="Client:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.client_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.client_var, foreground="#005fb8", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 15))
        
        ttk.Label(row1, text="Website:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.web_status_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.web_status_var, foreground="#2e86c1", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 15))

        ttk.Label(row1, text="Indexer:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.indexer_var = tk.StringVar(value="...")
        self.indexer_status_lbl = ttk.Label(row1, textvariable=self.indexer_var, font=('Segoe UI', 9, 'bold'))
        self.indexer_status_lbl.pack(side="left", padx=5)

        row2 = ttk.Frame(status_frame)
        row2.pack(fill="x", anchor="w", pady=(8, 0))
        ttk.Label(row2, text="Generation Preset:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.preset_var = tk.StringVar(value="...")
        ttk.Label(row2, textvariable=self.preset_var, foreground="#6c3483", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=10)

        # --- MAIN PANEL ---
        main_gen_frame = ttk.Frame(root)
        main_gen_frame.pack(fill="x", padx=15, pady=5)

        # Configuration (Left)
        conf_frame = ttk.LabelFrame(main_gen_frame, text=" Configuration ", padding="10")
        conf_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))

        ttk.Label(conf_frame, text="Client:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky="w")
        self.client_combo = ttk.Combobox(conf_frame, values=self.get_available_clients(), state="readonly", width=15)
        self.client_combo.grid(row=0, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.client_combo.bind("<<ComboboxSelected>>", self.apply_client_switch)

        ttk.Label(conf_frame, text="Website:", font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, sticky="w", pady=10)
        self.web_folder_var = tk.StringVar()
        self.web_folder_var.trace_add("write", self.check_web_changes)
        self.web_folder_entry = ttk.Entry(conf_frame, textvariable=self.web_folder_var, width=15)
        self.web_folder_entry.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=10)
        
        self.btn_web_upd = ttk.Button(conf_frame, text="Update Website", command=self.update_web_folder_in_ares)
        self.btn_web_upd.grid(row=1, column=2, padx=(5, 0), pady=10)

        ttk.Label(conf_frame, text="Preset:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky="w")
        self.preset_combo = ttk.Combobox(conf_frame, values=list({"HTML EN": "HTML_E", "HTML GR-EN": "HTML_GE", "HTML GR-EN / EN": "HTML_GE_E", "PDF EN": "PDF_E", "PDF GR-EN": "PDF_GE", "PDF GR": "PDF_G"}.keys()), state="readonly", width=15)
        self.preset_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)

        ttk.Label(conf_frame, text="Indexer:", font=('Segoe UI', 9, 'bold')).grid(row=3, column=0, sticky="w", pady=(10, 0))
        idx_btn_frame = ttk.Frame(conf_frame)
        idx_btn_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=(5, 0), pady=(10, 0))
        self.idx_state = tk.StringVar()
        tk.Radiobutton(idx_btn_frame, text="ON", font=('Segoe UI', 8), variable=self.idx_state, value="yes", indicatoron=0, width=5, command=lambda: self.set_indexer("yes")).pack(side="left")
        tk.Radiobutton(idx_btn_frame, text="OFF", font=('Segoe UI', 8), variable=self.idx_state, value="no", indicatoron=0, width=5, command=lambda: self.set_indexer("no")).pack(side="left")

        # Post-Generation (Right)
        post_frame = ttk.LabelFrame(main_gen_frame, text=" Post-Generation ", padding="10")
        post_frame.pack(side="left", fill="y", expand=False)

        ttk.Label(post_frame, text="PDF Covers:", font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        btn_logo = ttk.Button(post_frame, text="Add GOA Logo", style='Post.TButton', width=22, command=lambda: self.run_script(LOGO_SCRIPT))
        btn_logo.pack(pady=(5, 15))
        
        ttk.Label(post_frame, text="HTML Files:", font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        btn_goog = ttk.Button(post_frame, text="Insert Google Analytics", style='Post.TButton', width=22, command=lambda: self.run_script(ANALYTICS_SCRIPT))
        btn_goog.pack(pady=5)

        # --- LOG (Expands on Resize) ---
        self.log_frame = ttk.LabelFrame(root, text=" Activity Log ", padding="5")
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.console = scrolledtext.ScrolledText(self.log_frame, height=6, state='disabled', font=('Consolas', 9))
        self.console.pack(fill="both", expand=True)

        bottom_bar = ttk.Frame(root, padding=(15, 0, 15, 10))
        bottom_bar.pack(fill="x", side="bottom")
        self.btn_toggle = ttk.Button(bottom_bar, text="HIDE LOG", width=12, command=self.toggle_console)
        self.btn_toggle.pack(side="left")

        self.refresh_ui()

    def check_web_changes(self, *args):
        if self.web_folder_var.get() != self.web_status_var.get():
            self.btn_web_upd.configure(style='Alert.TButton')
        else: self.btn_web_upd.configure(style='TButton')

    def update_web_folder_in_ares(self):
        client, folder = self.client_combo.get(), self.web_folder_var.get().strip()
        path = self.find_ares_file(client)
        if not path or not folder: return
        try:
            with open(path, 'r', encoding='utf-8') as f: lines = f.readlines()
            with open(path, 'w', encoding='utf-8', newline='') as f:
                for line in lines:
                    if "generated.website.folder.root" in line: f.write(f'generated.website.folder.root = "{folder}/dcs"\n')
                    else: f.write(line)
            self.refresh_ui()
        except Exception as e: self.log(f"Error: {e}")

    def log(self, msg):
        self.console.config(state='normal'); self.console.insert(tk.END, f"> {msg}\n"); self.console.see(tk.END); self.console.config(state='disabled')

    def toggle_console(self):
        if self.log_frame.winfo_viewable():
            self.log_frame.pack_forget(); self.root.geometry(f"{self.root.winfo_width()}x{self.compact_height}")
        else:
            self.log_frame.pack(fill="both", expand=True, padx=15, pady=5); self.root.geometry(f"{self.root.winfo_width()}x{self.full_height}")

    def find_ares_file(self, client):
        target = f"pref.website_{client}.ares"
        for r, _, files in os.walk(CLIENTS_BASE):
            if target in files: return os.path.join(r, target)
        return None

    def refresh_ui(self):
        client = "..."
        if os.path.exists(CONTEXT_FILE):
            with open(CONTEXT_FILE, 'r') as f:
                client = f.read().strip()
                self.client_var.set(client.upper()); self.client_combo.set(client)
        path = self.find_ares_file(client)
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f: content = f.read()
                idx_match = re.search(r'generate\.services\.index\s*=\s*"([^"]+)"', content)
                if idx_match:
                    val = idx_match.group(1).lower()
                    self.indexer_var.set("ON" if val == "yes" else "OFF"); self.idx_state.set(val)
                    self.indexer_status_lbl.configure(foreground="green" if val == "yes" else "red")
                folder_match = re.search(r'generated\.website\.folder\.root\s*=\s*"([^/]+)/dcs"', content)
                if folder_match: 
                    self.web_status_var.set(folder_match.group(1)); self.web_folder_var.set(folder_match.group(1))
            except: pass
        if os.path.exists(PRESET_STATUS):
            with open(PRESET_STATUS, 'r') as f: self.preset_var.set(f.read().strip())
        self.check_web_changes()

    def get_available_clients(self):
        try: return [d for d in os.listdir(CLIENTS_BASE) if os.path.isdir(os.path.join(CLIENTS_BASE, d))]
        except: return []

    def apply_client_switch(self, event):
        client = self.client_combo.get()
        with open(CONTEXT_FILE, 'w') as f: f.write(client)
        threading.Thread(target=self.sync_master_ares, args=(client,), daemon=True).start()

    def sync_master_ares(self, client_name):
        try:
            with open(MASTER_ARES, 'r', encoding='utf-8') as f: content = f.read()
            pattern = r'(selected\.pref\.main\s*=\s*"pref\.main_)([^"]+)(")'
            if re.search(pattern, content):
                new_content = re.sub(pattern, rf'\1{client_name}\3', content)
                with open(MASTER_ARES, 'w', encoding='utf-8', newline='') as f: f.write(new_content)
        except Exception as e: self.log(f"Error: {e}")
        self.refresh_ui()

    def set_indexer(self, state): self.run_script(INDEXER_SCRIPT, state)
    def apply_preset(self, event):
        sel = self.preset_combo.get()
        self.run_script(PRESET_SCRIPT, {"HTML EN": "HTML_E", "HTML GR-EN": "HTML_GE", "HTML GR-EN / EN": "HTML_GE_E", "PDF EN": "PDF_E", "PDF GR-EN": "PDF_GE", "PDF GR": "PDF_G"}[sel])
        with open(PRESET_STATUS, 'w') as f: f.write(sel)
        self.refresh_ui()

    def run_script(self, script_path, arg=None):
        def worker():
            cmd = [sys.executable, script_path]
            if arg: cmd.append(arg)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:
                self.console.config(state='normal'); self.console.insert(tk.END, line); self.console.see(tk.END); self.console.config(state='disabled')
            p.wait(); self.refresh_ui()
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    tk_root = tk.Tk(); app = ALWBDashboard(tk_root); tk_root.mainloop()