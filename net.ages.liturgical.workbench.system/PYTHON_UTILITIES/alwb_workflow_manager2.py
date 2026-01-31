import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
ATEM_FILE = r"C:\git\ages-alwb-templates\net.ages.liturgical.workbench.templates\c-generator-settings\generator.atem"

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
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"), padx=5, pady=2)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class GenerationTab(ttk.Frame):
    def __init__(self, parent, log_callback):
        super().__init__(parent)
        self.log_callback = log_callback
        
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

        self.month_vars = {m[1]: tk.BooleanVar() for m in self.months_data}
        self.day_vars = {f"{d:02d}": tk.BooleanVar() for d in range(1, 32)}
        self.manual_var = tk.StringVar()

        for var in self.month_vars.values(): var.trace_add("write", self.on_input_change)
        for var in self.day_vars.values(): var.trace_add("write", self.on_input_change)
        self.manual_var.trace_add("write", self.set_button_dirty)

        self.create_widgets()
        self.sync_manual_box()

    def create_widgets(self):
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)

        m_frame = ttk.LabelFrame(container, text=" Months ", padding="5")
        m_frame.pack(fill="x", pady=(0, 5))
        m_grid = ttk.Frame(m_frame); m_grid.pack(anchor="w", pady=5)
        for i, (name, code) in enumerate(self.months_data):
            ttk.Checkbutton(m_grid, text=name, variable=self.month_vars[code]).grid(row=i//4, column=i%4, sticky="w", padx=5)

        d_frame = ttk.LabelFrame(container, text=" Days ", padding="5")
        d_frame.pack(fill="x", pady=5)
        d_grid = ttk.Frame(d_frame); d_grid.pack(anchor="w", pady=5)
        for d in range(1, 32):
            code = f"{d:02d}"
            row_idx = (d-1) // 10
            col_idx = (d-1) % 10
            ttk.Checkbutton(d_grid, text=code, variable=self.day_vars[code], width=4).grid(row=row_idx, column=col_idx, sticky="w", padx=2)

        s_frame = ttk.Frame(container); s_frame.pack(fill="x", pady=5)
        ttk.Label(s_frame, text="Preset:").grid(row=0, column=0, sticky="w")
        self.pattern_combo = ttk.Combobox(s_frame, values=list(self.regex_presets.keys()), state="readonly", width=18)
        self.pattern_combo.grid(row=0, column=1, padx=5); self.pattern_combo.set("HTML generation")
        self.pattern_combo.bind("<<ComboboxSelected>>", self.on_input_change)
        
        ttk.Label(s_frame, text="Status:").grid(row=0, column=2, padx=(10, 0))
        self.status_combo = ttk.Combobox(s_frame, values=self.status_options, state="readonly", width=8)
        self.status_combo.grid(row=0, column=3, padx=5); self.status_combo.set("Final")
        self.status_combo.bind("<<ComboboxSelected>>", self.set_button_dirty)

        r_frame = ttk.LabelFrame(container, text=" Final Regex (Review or Edit) ", padding="10")
        r_frame.pack(fill="x", pady=5)
        e_bar = ttk.Frame(r_frame); e_bar.pack(fill="x")
        ttk.Entry(e_bar, textvariable=self.manual_var, font=('Consolas', 10)).pack(side="left", fill="x", expand=True, padx=(0,5))
        
        self.btn_update_atem = tk.Button(e_bar, text="Update", command=self.update_atem, bg="#f0f0f0", relief="raised", bd=1, width=8)
        self.btn_update_atem.pack(side="left", padx=2)
        ToolTip(self.btn_update_atem, "Update generator.atem with these settings")
        
        ttk.Button(e_bar, text="Revert", command=self.sync_manual_box, width=8).pack(side="left", padx=(2, 0))

    def on_input_change(self, *args):
        self.sync_manual_box()
        self.set_button_dirty()

    def set_button_dirty(self, *args):
        self.btn_update_atem.configure(bg="red", fg="white", font=('Segoe UI', 9, 'bold'))

    def set_button_clean(self):
        self.btn_update_atem.configure(bg="#f0f0f0", fg="black", font=('Segoe UI', 9))

    def sync_manual_box(self, *args):
        sel_m = sorted([c for c, v in self.month_vars.items() if v.get()])
        sel_d = sorted([c for c, v in self.day_vars.items() if v.get()])
        m_p = self.build_grp(sel_m, 12); d_p = self.build_grp(sel_d, 31)
        self.manual_var.set(self.regex_presets[self.pattern_combo.get()].format(m=m_p, d=d_p))
        self.set_button_clean()

    def build_grp(self, items, count):
        if len(items) == count or len(items) == 0: return "(..)"
        return f"({items[0]})" if len(items) == 1 else f"({'|'.join(items)})"

    def update_atem(self):
        try:
            regex = self.manual_var.get().strip()
            line_reg = f'\t\tService_Regular_Expression "{regex}.atem"\n'
            line_stat = f'\t\tService_Status {self.status_combo.get()}\n'
            with open(ATEM_FILE, 'r', encoding='utf-8') as f: lines = f.readlines()
            with open(ATEM_FILE, 'w', encoding='utf-8', newline='') as f:
                for l in lines:
                    if "Service_Regular_Expression" in l: f.write(line_reg)
                    elif "Service_Status" in l: f.write(line_stat)
                    else: f.write(l)
            messagebox.showinfo("Success", "Atem file updated.")
            self.log_callback(f"generator.atem updated: {regex}")
            self.set_button_clean()
        except Exception as e: messagebox.showerror("Error", str(e))

class ALWBWorkflowManager:
    def __init__(self, root):
        self.root = root
        try:
            self.logo_img = tk.PhotoImage(file=LOGO_ICON_PATH)
            self.root.iconphoto(False, self.logo_img)
        except:
            pass
        self.root.title("DCS Generation Dashboard")
        self.root.geometry("550x750")
        self.root.resizable(True, True)
        self.root.minsize(440, 480)

        self.style = ttk.Style()
        self.style.theme_use('xpnative')

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text=" Who - Where - How ")
        self.setup_main_tab()

        self.gen_tab = GenerationTab(self.notebook, self.log)
        self.notebook.add(self.gen_tab, text=" What ")

        self.log_frame = ttk.LabelFrame(self.main_container, text=" Activity Log ", padding="5")
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.console = scrolledtext.ScrolledText(self.log_frame, height=5, state='disabled', font=('Consolas', 9))
        self.console.pack(fill="both", expand=True)

        footer = ttk.Frame(self.main_container, padding=(15, 0, 15, 10))
        footer.pack(fill="x", side="bottom")
        self.btn_log_toggle = ttk.Button(footer, text="HIDE LOG", width=12, command=self.toggle_log)
        self.btn_log_toggle.pack(side="left")

        self.refresh_ui()

    def toggle_log(self):
        if self.log_frame.winfo_viewable():
            self.log_frame.pack_forget()
            self.btn_log_toggle.configure(text="SHOW LOG")
        else:
            self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
            self.btn_log_toggle.configure(text="HIDE LOG")

    def setup_main_tab(self):
        status_frame = ttk.LabelFrame(self.main_tab, text=" System Status ", padding="10")
        status_frame.pack(fill="x", padx=15, pady=5)
        
        row1 = ttk.Frame(status_frame); row1.pack(fill="x")
        ttk.Label(row1, text="Client:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.client_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.client_var, foreground="#005fb8", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 10))
        
        ttk.Label(row1, text="Website:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.web_status_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.web_status_var, foreground="#2e86c1", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 10))
        
        ttk.Label(row1, text="Indexer:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.indexer_var = tk.StringVar(value="...")
        self.indexer_status_lbl = ttk.Label(row1, textvariable=self.indexer_var, font=('Segoe UI', 9, 'bold'))
        self.indexer_status_lbl.pack(side="left", padx=5)

        row2 = ttk.Frame(status_frame); row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="Generation Preset:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.preset_var = tk.StringVar(value="...")
        ttk.Label(row2, textvariable=self.preset_var, foreground="#6c3483", font=('Segoe UI', 9, 'bold')).pack(side="left", padx=10)

        conf_frame = ttk.LabelFrame(self.main_tab, text=" Configuration ", padding="10")
        conf_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(conf_frame, text="Client:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky="w")
        self.client_combo = ttk.Combobox(conf_frame, values=self.get_available_clients(), state="readonly", width=15)
        self.client_combo.grid(row=0, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.client_combo.bind("<<ComboboxSelected>>", self.apply_client_switch)

        ttk.Label(conf_frame, text="Website:", font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, sticky="w", pady=10)
        self.web_folder_var = tk.StringVar()
        self.web_folder_var.trace_add("write", self.handle_web_change) 
        self.web_folder_entry = ttk.Entry(conf_frame, textvariable=self.web_folder_var, width=15)
        self.web_folder_entry.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=10)
        
        self.btn_update_web = tk.Button(conf_frame, text="Update Website", command=self.update_web_folder_in_ares, width=15, relief="raised", bd=1, bg="#f0f0f0")
        self.btn_update_web.grid(row=1, column=2, padx=(5,0), pady=10)
        ToolTip(self.btn_update_web, "Update the website folder root for this client")

        ttk.Label(conf_frame, text="Preset:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky="w")
        self.preset_combo = ttk.Combobox(conf_frame, values=["HTML EN", "HTML GR-EN", "HTML GR-EN / EN", "PDF EN", "PDF GR-EN", "PDF GR"], state="readonly", width=15)
        self.preset_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)
        
        ttk.Label(conf_frame, text="Indexer:", font=('Segoe UI', 9, 'bold')).grid(row=3, column=0, sticky="w", pady=(10, 0))
        idx_btn_frame = ttk.Frame(conf_frame); idx_btn_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=(5, 0), pady=(10, 0))
        self.idx_state = tk.StringVar()
        tk.Radiobutton(idx_btn_frame, text="ON", variable=self.idx_state, value="yes", indicatoron=0, width=5, command=lambda: self.set_indexer("yes")).pack(side="left")
        tk.Radiobutton(idx_btn_frame, text="OFF", variable=self.idx_state, value="no", indicatoron=0, width=5, command=lambda: self.set_indexer("no")).pack(side="left")

        post_frame = ttk.LabelFrame(self.main_tab, text=" Post-Generation ", padding="10")
        post_frame.pack(fill="x", padx=15, pady=5)
        
        tight_row = ttk.Frame(post_frame); tight_row.pack(fill="x")
        ttk.Label(tight_row, text="PDF:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.btn_logo = ttk.Button(tight_row, text="Add Logo", command=lambda: self.run_script(LOGO_SCRIPT), width=9)
        self.btn_logo.pack(side="left", padx=(2, 10))
        ToolTip(self.btn_logo, "Add GOA logo to PDF covers")

        ttk.Label(tight_row, text="HTML:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.btn_code = ttk.Button(tight_row, text="Insert Code", command=lambda: self.run_script(ANALYTICS_SCRIPT), width=10)
        self.btn_code.pack(side="left", padx=2)
        ToolTip(self.btn_code, "Insert google analytics code into HTML files")

    def handle_web_change(self, *args):
        if self.web_folder_var.get() != self.web_status_var.get():
             self.btn_update_web.configure(bg="red", fg="white", font=('Segoe UI', 9, 'bold'))
        else:
             self.btn_update_web.configure(bg="#f0f0f0", fg="black", font=('Segoe UI', 9))

    def log(self, msg):
        self.console.config(state='normal'); self.console.insert(tk.END, f"> {msg}\n"); self.console.see(tk.END); self.console.config(state='disabled')

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
                f_match = re.search(r'generated\.website\.folder\.root\s*=\s*"([^/]+)/dcs"', content)
                if f_match: 
                    current_val = f_match.group(1)
                    self.web_status_var.set(current_val)
                    self.web_folder_var.set(current_val)
                    self.btn_update_web.configure(bg="#f0f0f0", fg="black", font=('Segoe UI', 9))
            except: pass
        if os.path.exists(PRESET_STATUS):
            with open(PRESET_STATUS, 'r') as f: self.preset_var.set(f.read().strip())

    def find_ares_file(self, client):
        target = f"pref.website_{client}.ares"
        for r, _, files in os.walk(CLIENTS_BASE):
            if target in files: return os.path.join(r, target)
        return None

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
            self.refresh_ui(); messagebox.showinfo("Updated", f"Website folder set to: {folder}")
        except Exception as e: self.log(f"Error: {e}")

    def set_indexer(self, state): self.run_script(INDEXER_SCRIPT, state)
    def apply_preset(self, event):
        sel = self.preset_combo.get()
        mapping = {"HTML EN": "HTML_E", "HTML GR-EN": "HTML_GE", "HTML GR-EN / EN": "HTML_GE_E", "PDF EN": "PDF_E", "PDF GR-EN": "PDF_GE", "PDF GR": "PDF_G"}
        self.run_script(PRESET_SCRIPT, mapping[sel])
        with open(PRESET_STATUS, 'w') as f: f.write(sel)
        self.refresh_ui()

    def run_script(self, script_path, arg=None):
        def worker():
            cmd = [sys.executable, script_path]
            if arg: cmd.append(arg)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout: self.log(line.strip())
            p.wait(); self.refresh_ui()
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    tk_root = tk.Tk(); app = ALWBWorkflowManager(tk_root); tk_root.mainloop()