import automate_generation
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sys
import re
import threading
from pathlib import Path
from datetime import datetime
from path_settings import (
    LOGO_ICON_PATH, CONTEXT_FILE, PRESET_STATUS, 
    MASTER_ARES, CLIENTS_BASE, ATEM_FILE, 
    DERIVED_WEBSITE_BASE, SCAN_PATH,
    BASE_PATH, UTILS_DIR, GIT_FOLDER, DRIVE_ROOT, 
    JAVA_EXE, TOOLS_BASE
)

# --- SHARED PATHS ---
from path_settings import (
    LOGO_ICON_PATH, CONTEXT_FILE, PRESET_STATUS, 
    MASTER_ARES, CLIENTS_BASE, ATEM_FILE, 
    DERIVED_WEBSITE_BASE, SCAN_PATH,
    BASE_PATH
)

# Worker Scripts
PRESET_SCRIPT = os.path.join(BASE_PATH, "preset_switcher.py")
LOGO_SCRIPT = os.path.join(BASE_PATH, "add_logo.py")
ANALYTICS_SCRIPT = os.path.join(BASE_PATH, "insert_google_analytics.py")
INDEXER_SCRIPT = os.path.join(BASE_PATH, "toggle_client_indexer.py")
CHECK_STATUS_SCRIPT = os.path.join(BASE_PATH, "check_template_status.py")

# --- UI COMPONENT CLASSES ---


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


class WhatTab(ttk.Frame):
    def __init__(self, parent, run_script_callback, manager):
        super().__init__(parent)
        self.run_script = run_script_callback
        self.manager = manager
        container = ttk.Frame(self, padding="20")
        container.pack(fill="both", expand=True)

        v_frame = ttk.LabelFrame(container, text=" Template Readiness (What) ", padding="15")
        v_frame.pack(fill="x", pady=10)
        ttk.Label(v_frame, text="Select a month to check its templates.").pack(anchor="w")
        self.val_months_data = [
            ("January", "m01"), ("February", "m02"), ("March", "m03"), ("April", "m04"),
            ("May", "m05"), ("June", "m06"), ("July", "m07"), ("August", "m08"),
            ("September", "m09"), ("October", "m10"), ("November", "m11"), ("December", "m12")
        ]
        self.val_month_combo = ttk.Combobox(
            v_frame, values=[m[0] for m in self.val_months_data], state="readonly")
        self.val_month_combo.pack(pady=10, fill="x")
        self.val_month_combo.set("January")
        self.btn_check = ttk.Button(v_frame, text="Run Validation Report",
                                    command=self.trigger_validation, width=25)
        self.btn_check.pack(pady=5, anchor="w")

        w_frame = ttk.LabelFrame(container, text=" Website Readiness ", padding="15")
        w_frame.pack(fill="x", pady=10)
        ttk.Label(w_frame, text="Sacraments and Services Index",
                  font=('Segoe UI', 9, 'bold')).pack(anchor="w")
        self.btn_index_books = ttk.Button(w_frame, text="Update EN and GR Media",
                                          command=lambda: self.run_script("total_media_refresh.py"), width=25)
        self.btn_index_books.pack(pady=5, anchor="w")

        t_frame = ttk.LabelFrame(container, text=" Template Testing ", padding="15")
        t_frame.pack(fill="x", pady=10)
        ttk.Label(t_frame, text="1. Click the Test Settings button to set client to 'test' and generation to HTML EN.").pack(anchor="w")
        self.btn_prep = ttk.Button(t_frame, text="Test Settings",
                                   command=self.manager.setup_test_env, width=25)
        self.btn_prep.pack(pady=5, anchor="w")
        ToolTip(self.btn_prep, "Sets Client=test, Indexer=OFF, Preset=HTML EN, targets Month, and opens ATEM")

        # Step 2
        ttk.Label(
                t_frame, 
                text="2. Click the Run Generator button to generate the services of the selected month. Eclipse will seem to hang and indicate that is Not Responding. This is normal.",
                wraplength=400,
                justify="left"
        ).pack(anchor="w", pady=(10, 0))
        self.btn_generate = ttk.Button(t_frame, text="Run Generator",
                                       command=self.trigger_eclipse_generation, width=25)
        self.btn_generate.pack(pady=5, anchor="w")
        ToolTip(self.btn_generate, "Focuses Eclipse Oxygen.2 and executes the Ctrl+G macro automatically")

        # Step 3
        ttk.Label(
            t_frame, 
            text="3. After the files have been generated and Eclipse is responding again, click the Scan for Missing Strings button. The results of the scan will appear in the Activity Log.",
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))
        
        self.btn_scan = ttk.Button(t_frame, text="Scan for Missing Strings",
                                   command=self.manager.run_error_scan, width=25)
        self.btn_scan.pack(pady=5, anchor="w")

    def trigger_eclipse_generation(self):
        from tkinter import messagebox
        success, message = automate_generation.run_generator_macro()
        if success:
            messagebox.showinfo("Eclipse Automation", "Ctrl+G sent successfully!\nCheck Oxygen.2 for generation progress.")
        else:
            messagebox.showerror("Automation Error", f"Failed to trigger Eclipse:\n{message}")

    def trigger_validation(self):
        selected_name = self.val_month_combo.get()
        month_code = next(m[1] for m in self.val_months_data if m[0] == selected_name)
        self.run_script(CHECK_STATUS_SCRIPT, month_code)

class WhenTab(ttk.Frame):
    def __init__(self, parent, log_callback):
        super().__init__(parent)
        self.log_callback = log_callback
        self.months_data = [("January", "01"), ("February", "02"), ("March", "03"), ("April", "04"), ("May", "05"), ("June", "06"), (
            "July", "07"), ("August", "08"), ("September", "09"), ("October", "10"), ("November", "11"), ("December", "12")]
        self.status_options = ["Final", "Review", "Draft", "NA"]
        self.regex_presets = {
            "For HTML generation": r"se.m{m}.d{d}.(..|...)", "For PDF generation": r"se.m{m}.d{d}.(..|(?!(ma2|h91))\\w{{3}})", "For Seminary Chapel generation": r"se.hc.m{m}.d{d}.(ma8)"}
        self.month_vars = {m[1]: tk.BooleanVar() for m in self.months_data}
        self.day_vars = {f"{d:02d}": tk.BooleanVar() for d in range(1, 32)}
        self.manual_var = tk.StringVar()
        for var in self.month_vars.values():
            var.trace_add("write", self.on_input_change)
        for var in self.day_vars.values():
            var.trace_add("write", self.on_input_change)
        self.manual_var.trace_add("write", self.set_button_dirty)
        self.create_widgets()
        self.sync_manual_box()

    def run_pdf_transformer(self):
        """Launches the Java Transformer with specific pathing for the 'bin' root."""
        self.log_callback(">>> Initializing PDF Transformer (C: Drive)")
        
        try:
            # 1. PATH CONFIGURATION
            java_exe = r"C:\Program Files\Java\jre1.8.0_461\bin\java.exe"
            working_dir = r"C:\ALWB_Additional_Resources\dcsjavautilities"
            
            # The root of your compiled classes
            bin_dir = os.path.join(working_dir, "bin")
            
            # The full name of the class (Package + ClassName)
            main_class = "net.ages.liturgical.workbench.transformer.AlwbTransformer" 
            
            # 2. BUILD THE CLASSPATH
            # Note: We point to 'bin', not 'bin/net/ages...'
            cp_parts = [
                bin_dir,
                os.path.join(working_dir, "lib", "jars", "*"),
                os.path.join(working_dir, "lib", "fop-1.1", "build", "fop.jar"),
                os.path.join(working_dir, "lib", "fop-1.1", "lib", "*")
            ]
            full_classpath = ";".join(cp_parts)

            # 3. EXECUTION
            self.log_callback(f"STATUS: Executing {main_class}...")
            
            # Using Popen with stdout capture to see Java's internal messages
            process = subprocess.Popen(
                [java_exe, "-Dfile.encoding=UTF-8", "-cp", full_classpath, main_class],
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # 4. MONITOR OUTPUT IN REAL-TIME
            def stream_output():
                for line in iter(process.stdout.readline, ''):
                    self.log_callback(f"JAVA: {line.strip()}")
                process.stdout.close()
                return_code = process.wait()
                if return_code == 0:
                    self.log_callback("SUCCESS: PDF Transformation sequence complete.")
                else:
                    self.log_callback(f"ERROR: Java exited with code {return_code}")

            import threading
            threading.Thread(target=stream_output, daemon=True).start()

        except Exception as e:
            self.log_callback(f"CRITICAL ERROR: {str(e)}")

    def create_widgets(self):
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)
        
        # Months Section
        m_frame = ttk.LabelFrame(container, text=" Months ", padding="5")
        m_frame.pack(fill="x", pady=(0, 5))
        m_grid = ttk.Frame(m_frame)
        m_grid.pack(anchor="w", pady=5)
        for i, (name, code) in enumerate(self.months_data):
            ttk.Checkbutton(m_grid, text=name, variable=self.month_vars[code]).grid(
                row=i//4, column=i % 4, sticky="w", padx=5)
        
        # Days Section
        d_frame = ttk.LabelFrame(container, text=" Days ", padding="5")
        d_frame.pack(fill="x", pady=5)
        d_grid = ttk.Frame(d_frame)
        d_grid.pack(anchor="w", pady=5)
        for d in range(1, 32):
            code = f"{d:02d}"
            ttk.Checkbutton(d_grid, text=code, variable=self.day_vars[code], width=4).grid(
                row=(d-1)//10, column=(d-1) % 10, sticky="w", padx=2)
        
        # Settings Section
        s_frame = ttk.Frame(container)
        s_frame.pack(fill="x", pady=5)
        ttk.Label(s_frame, text="Preset:").grid(row=0, column=0, sticky="w")
        self.pattern_combo = ttk.Combobox(s_frame, values=list(
            self.regex_presets.keys()), state="readonly", width=30)
        self.pattern_combo.grid(row=0, column=1, padx=5)
        self.pattern_combo.set("For HTML generation")
        self.pattern_combo.bind("<<ComboboxSelected>>", self.on_input_change)
        
        ttk.Label(s_frame, text="Status:").grid(row=0, column=2, padx=(10, 0))
        self.status_combo = ttk.Combobox(
            s_frame, values=self.status_options, state="readonly", width=8)
        self.status_combo.grid(row=0, column=3, padx=5)
        self.status_combo.set("Final")
        self.status_combo.bind("<<ComboboxSelected>>", self.set_button_dirty)
        
        # Regex Editor Section
        r_frame = ttk.LabelFrame(container, text=" Final Regex (Review or Edit) ", padding="10")
        r_frame.pack(fill="x", pady=5)
        e_bar = ttk.Frame(r_frame)
        e_bar.pack(fill="x")
        ttk.Entry(e_bar, textvariable=self.manual_var, font=('Consolas', 10)
                  ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_update_atem = tk.Button(
            e_bar, text="Update", command=self.update_atem, bg="#f0f0f0", relief="raised", bd=1, width=8)
        self.btn_update_atem.pack(side="left", padx=2)
        ToolTip(self.btn_update_atem, "Update generator.atem with these settings")
        ttk.Button(e_bar, text="Revert", command=self.sync_manual_box,
                   width=8).pack(side="left", padx=(2, 0))

        # --- Section 4: Transformer for PDFs ---
        self.pdf_frame = ttk.LabelFrame(container, text=" Transformer for PDFs ", padding="10")
        self.pdf_frame.pack(fill="x", pady=5)

        # Original Step 1 Label
        ttk.Label(
            self.pdf_frame, 
            text="Step 1: Click the Run Generator button to generate the selected services. Eclipse will seem to hang and indicate that it is Not Responding. This is normal.", 
            foreground="black", 
            font=('Segoe UI', 9),
            justify="left",
            wraplength=350
        ).pack(pady=(5, 2), anchor="w", padx=10)

        # New Generation Button
        self.btn_generate_pdf = ttk.Button(
            self.pdf_frame, 
            text="Run Generator",
            command=self.trigger_eclipse_generation, 
            width=20
        )
        self.btn_generate_pdf.pack(pady=5, padx=10, anchor="w")

        # Original Step 2 Label
        ttk.Label(
            self.pdf_frame, 
            text="Step 2: When generation has finished (i.e. Eclipse is responding again), click the Run PDF Transformer button to transform the generated .fo files into .pdf.", 
            foreground="black", 
            font=('Segoe UI', 9),
            justify="left",
            wraplength=350
        ).pack(pady=(2, 5), anchor="w", padx=10)

        self.btn_run_transformer = ttk.Button(
            self.pdf_frame,
            text="Run PDF Transformer",
            command=self.run_pdf_transformer,
            width=20
        )
        self.btn_run_transformer.pack(pady=5, padx=10, anchor="w")

    # Required method for the button to work
    def trigger_eclipse_generation(self):
        from tkinter import messagebox
        import automate_generation
        success, message = automate_generation.run_generator_macro()
        if success:
            messagebox.showinfo("Eclipse Automation", "Ctrl+G sent successfully!\nCheck Oxygen.2 for generation progress.")
        else:
            messagebox.showerror("Automation Error", f"Failed to trigger Eclipse:\n{message}")

    def on_input_change(self, *args): self.sync_manual_box(); self.set_button_dirty()

    def set_button_dirty(self, *args): self.btn_update_atem.configure(bg="red",
                                                                    fg="white", font=('Segoe UI', 9, 'bold'))

    def set_button_clean(self): self.btn_update_atem.configure(
        bg="#f0f0f0", fg="black", font=('Segoe UI', 9))

    def sync_manual_box(self, *args):
        sel_m = sorted([c for c, v in self.month_vars.items() if v.get()])
        sel_d = sorted([c for c, v in self.day_vars.items() if v.get()])
        m_p = self.build_grp(sel_m, 12)
        d_p = self.build_grp(sel_d, 31)
        self.manual_var.set(self.regex_presets[self.pattern_combo.get()].format(m=m_p, d=d_p))
        self.set_button_clean()

    def build_grp(self, items, count):
        if len(items) == count or len(items) == 0:
            return "(..)"
        return f"({items[0]})" if len(items) == 1 else f"({'|'.join(items)})"

    def update_atem(self):
        try:
            regex, stat = self.manual_var.get().strip(), self.status_combo.get()
            with open(ATEM_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(ATEM_FILE, 'w', encoding='utf-8', newline='') as f:
                for l in lines:
                    if "Service_Regular_Expression" in l:
                        f.write(f'\t\tService_Regular_Expression "{regex}.atem"\n')
                    elif "Service_Status" in l:
                        f.write(f'\t\tService_Status {stat}\n')
                    else:
                        f.write(l)
            messagebox.showinfo("Success", "Atem file updated.")
            self.log_callback(f"generator.atem updated: {regex}")
            self.set_button_clean()
            if os.path.exists(ATEM_FILE):
                os.startfile(ATEM_FILE)
        except Exception as e:
            messagebox.showerror("Error", str(e))

class PostGenerationTab(ttk.Frame):
    def __init__(self, parent, log_callback, run_script_callback):
        super().__init__(parent)
        self.log_callback = log_callback
        self.run_script = run_script_callback
        self.service_rows = []
        self.current_file = None
        container = ttk.Frame(self, padding="10")
        container.pack(fill="both", expand=True)
        util_frame = ttk.LabelFrame(container, text=" Post-Generation Utilities ", padding="10")
        util_frame.pack(fill="x", pady=(0, 5))
        tight_row = ttk.Frame(util_frame)
        tight_row.pack(fill="x")
        ttk.Label(tight_row, text="PDF:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        btn_logo = ttk.Button(tight_row, text="Add Logo",
                              command=lambda: self.run_script(LOGO_SCRIPT), width=9)
        btn_logo.pack(side="left", padx=(2, 10))
        ttk.Label(tight_row, text="HTML:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        btn_code = ttk.Button(tight_row, text="Insert Code",
                              command=lambda: self.run_script(ANALYTICS_SCRIPT), width=10)
        btn_code.pack(side="left", padx=2)
        editor_frame = ttk.LabelFrame(container, text=" Index Editor ", padding="10")
        editor_frame.pack(fill="both", expand=True, pady=5)
        sel_frame = ttk.Frame(editor_frame)
        sel_frame.pack(fill="x", pady=(0, 5))
        sites = sorted([d.name for d in DERIVED_WEBSITE_BASE.iterdir() if d.is_dir()]
                       ) if DERIVED_WEBSITE_BASE.exists() else ["Error"]
        self.site_combo = ttk.Combobox(sel_frame, values=sites, state="readonly", width=12)
        self.site_combo.pack(side="left", padx=5)
        if "goa" in sites:
            self.site_combo.set("goa")
        self.y_var, self.m_var, self.d_var = tk.StringVar(value="2026"), tk.StringVar(
            value=datetime.now().strftime("%m")), tk.StringVar(value=datetime.now().strftime("%d"))
        ttk.Combobox(sel_frame, textvariable=self.y_var, values=[
                     str(y) for y in range(2024, 2030)], width=6).pack(side="left")
        ttk.Combobox(sel_frame, textvariable=self.m_var, values=[
                     f"{m:02d}" for m in range(1, 13)], width=4).pack(side="left", padx=2)
        ttk.Combobox(sel_frame, textvariable=self.d_var, values=[
                     f"{d:02d}" for d in range(1, 32)], width=4).pack(side="left")
        ttk.Button(sel_frame, text="Load", command=self.load_index,
                   width=8).pack(side="left", padx=10)
        ttk.Button(sel_frame, text="Save All", command=self.save_index, width=10).pack(side="left")
        self.canvas = tk.Canvas(editor_frame)
        self.scrollbar = ttk.Scrollbar(editor_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_index(self):
        fname = f"{self.y_var.get()}{self.m_var.get()}{self.d_var.get()}.html"
        self.current_file = DERIVED_WEBSITE_BASE / self.site_combo.get() / "dcs" / "indexes" / fname
        if not self.current_file.exists():
            messagebox.showerror("Not Found", f"Derived index missing:\n{fname}")
            return
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.service_rows = []
        content = self.current_file.read_text(encoding="utf-8")
        matches = re.finditer(r"<span class='index-service-day'>(.*?)</span>", content)
        for m in matches:
            row = ttk.Frame(self.scroll_frame, padding=2)
            row.pack(fill="x")
            e = ttk.Entry(row, width=60)
            e.insert(0, m.group(1))
            e.pack(side="left", padx=5)
            self.service_rows.append({'orig': m.group(1), 'entry': e})
        self.log_callback(f"Loaded index for editing: {fname}")

    def save_index(self):
        if not self.current_file:
            return
        content = self.current_file.read_text(encoding="utf-8")
        for r in self.service_rows:
            content = content.replace(
                f"class='index-service-day'>{r['orig']}</span>", f"class='index-service-day'>{r['entry'].get()}</span>")
        self.current_file.write_text(content, encoding="utf-8")
        messagebox.showinfo("Saved", "Derived index updated.")
        self.load_index()

# --- MAIN APPLICATION MANAGER ---


class ALWBWorkflowManager:
    def __init__(self, root):
        self.root = root
        try:
            self.logo_img = tk.PhotoImage(file=LOGO_ICON_PATH)
            self.root.iconphoto(False, self.logo_img)
        except:
            pass
        self.root.title("DCS Generation Dashboard")
        self.root.geometry("600x900")
        self.root.attributes("-topmost", True)
        self.root.resizable(True, True)
        self.root.minsize(440, 480)
        self.style = ttk.Style()
        self.style.theme_use('xpnative')
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- TAB SETUP ---
        self.what_tab = WhatTab(self.notebook, self.run_script, self)
        self.notebook.add(self.what_tab, text=" What ")

        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text=" Who - Where - How ")
        self.setup_main_tab()

        self.when_tab = WhenTab(self.notebook, self.log)
        self.notebook.add(self.when_tab, text=" When ")

        self.post_gen_tab = PostGenerationTab(self.notebook, self.log, self.run_script)
        self.notebook.add(self.post_gen_tab, text=" Post-Generation ")

        # --- LOGGING UI ---
        self.log_container = ttk.Frame(self.main_container)
        self.log_container.pack(fill="both", expand=True)
        self.button_bar = ttk.Frame(self.log_container)
        self.button_bar.pack(fill="x", padx=15)
        ttk.Button(self.button_bar, text="CLEAR", width=10,
                   command=self.clear_log).pack(side="right", padx=2)
        self.btn_log_toggle = ttk.Button(
            self.button_bar, text="HIDE LOG", width=12, command=self.toggle_log)
        self.btn_log_toggle.pack(side="right", padx=2)
        self.log_frame = ttk.LabelFrame(self.log_container, text=" Activity Log ", padding="5")
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
        # Standard Console Setup
        self.console = scrolledtext.ScrolledText(
            self.log_frame,
            height=15,
            state='disabled',
            font=('Consolas', 10),
            bg="#000000",       # Black Background
            fg="#FFFFFF",       # White Text
            insertbackground="white"
        )
        self.console.pack(fill="both", expand=True)
        self.refresh_ui()

    # -------------------------------------------------------------------------
    # BAKED-IN LOGIC SECTION (Functionality moved here for organization)
    # -------------------------------------------------------------------------

    def setup_test_env(self):
        """Action for 'Test for Empty Strings' - Prepares all systems and focuses Eclipse"""
        self.log("Template Testing setup: Overriding configuration for Empty String check...")
        try:
            with open(CONTEXT_FILE, 'w') as f:
                f.write("test")
            self.log("CLIENT: Set to 'test' (This changed the file 'pref.master.templates.ares')")
            self.set_indexer("no")
            mapping = {"HTML EN": "HTML_E"}
            self.run_script(PRESET_SCRIPT, mapping["HTML EN"])
            with open(PRESET_STATUS, 'w') as f:
                f.write("HTML EN")
            selected_name = self.what_tab.val_month_combo.get()
            month_code = next(m[1] for m in self.what_tab.val_months_data if m[0] == selected_name)
            pattern = f"se.{month_code}.d(..).(..|...)"
            with open(ATEM_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(ATEM_FILE, 'w', encoding='utf-8', newline='') as f:
                for line in lines:
                    if "Service_Regular_Expression" in line:
                        f.write(f'\t\tService_Regular_Expression "{pattern}.atem"\n')
                    else:
                        f.write(line)
            os.utime(ATEM_FILE, None)
            self.log(f"SYNC: to selected month (The regular expression in the file 'generator.atem' is set to {selected_name} i.e. {month_code})")
            self.refresh_ui()
            if os.path.exists(ATEM_FILE):
                os.startfile(ATEM_FILE)
                self.log(f"ECLIPSE: Opens file {os.path.basename(ATEM_FILE)}")
            self.log("--------------------------------------------------")
            self.log("SYSTEM READY: Click inside the generator.atem file now open in Eclipse, and press CTRL+G to generate.")
            self.log("--------------------------------------------------")
        except Exception as e:
            self.log(f"ERROR in setup_test_env: {e}")

    def run_error_scan(self):
        """Scans 'en' folders only, skipping Greek/Bilingual false positives"""
        search_strings = ["<p class='hymn'><span class='kvp dummy'",
                          "<p class='reading'><span class='kvp dummy'"]
        found_count = 0
        self.log(f"SCANNING: Filtering English paths in {SCAN_PATH}...")
        if not SCAN_PATH.exists():
            self.log(f"ERROR: Scan path missing: {SCAN_PATH}")
            return
        for html_file in SCAN_PATH.rglob("index.html"):
            path_parts = [p.lower() for p in html_file.parts]
            if any(x in path_parts for x in ["gr", "gr-en", "grem"]) or "en" not in path_parts:
                continue
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        if any(s in line for s in search_strings):
                            rel_p = str(html_file.parent.relative_to(SCAN_PATH)).replace("\\", "/")
                            self.log_link(f"{rel_p} (Line {i})", str(html_file))
                            found_count += 1
                            break
            except Exception as e:
                self.log(f"Read Error: {html_file.name}")
        if found_count == 0:
            self.log("SUCCESS: No missing strings found in English folders.")
            messagebox.showinfo("QA Pass", "Clean English Generation!")
        else:
            self.log(f"SCAN COMPLETE: {found_count} issues reported.")

    def log_link(self, msg, file_path):
        self.console.config(state='normal')
        tag_name = f"link_{hash(file_path)}"

        # Updated for high-contrast visibility on black background
        self.console.tag_config(tag_name, foreground="#66B2FF", underline=1, font=('Consolas', 10))

        self.console.insert(tk.END, f">   - {msg}\n", tag_name)

        # Using p=file_path to ensure the correct path is captured in the lambda
        self.console.tag_bind(tag_name, "<Button-1>", lambda e, p=file_path: os.startfile(p))
        self.console.tag_bind(tag_name, "<Enter>", lambda e: self.console.config(cursor="hand2"))
        self.console.tag_bind(tag_name, "<Leave>", lambda e: self.console.config(cursor=""))

        self.console.see(tk.END)
        self.console.config(state='disabled')

    def log(self, msg):
        self.console.config(state='normal')
        # Configured for high visibility on black background
        self.console.tag_config("mismatch", foreground="#FF3333", font=('Consolas', 10, 'bold'))

        # Apply the red tag if "MISMATCH", "ERROR", or "FAIL" is found
        tag = "mismatch" if any(x in msg.upper() for x in ["MISMATCH", "ERROR", "FAIL"]) else None

        self.console.insert(tk.END, f"> {msg}\n", tag)
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def run_script(self, script_path, arg=None):
        def worker():
            # Locked to GIT_FOLDER on C: drive via path_settings
            template_base = Path(GIT_FOLDER) / "ages-alwb-templates" / "net.ages.liturgical.workbench.templates" / "a-templates" / "Dated-Services"

            if script_path == "total_media_refresh.py":
                # Media indexer located on C: drive via system repo
                media_folder = os.path.join(GIT_FOLDER, "ages-alwb-system", "net.ages.liturgical.workbench.system", "MEDIA_INDEX_UTILITY", "python_code")
                final_path = os.path.join(media_folder, script_path)
            elif not os.path.isabs(script_path):
                final_path = os.path.join(UTILS_DIR, script_path)
            else:
                final_path = script_path
            if os.path.exists(final_path):
                self.log(f"Launching Utility: {os.path.basename(final_path)}")
                cmd = [sys.executable, final_path]
                if arg:
                    cmd.append(arg)

                p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True)

                for line in p.stdout:
                    clean_line = line.strip()
                    # Regex to find filenames like: se.m01.d01.h91.atem
                    match = re.search(r'(se\.(m\d{2})\.(d\d{2})\..*?\.atem)', clean_line)

                    if match:
                        full_filename = match.group(1)  # se.m01.d01.h91.atem
                        month_part = match.group(2)    # m01
                        day_part = match.group(3)      # d01

                        # Build the nested path on C: ...\Dated-Services\m01\d01\se.m01.d01.h91.atem
                        full_file_path = template_base / month_part / day_part / full_filename

                        if full_file_path.exists():
                            self.log_link(clean_line, str(full_file_path))
                        else:
                            # If for some reason the dXX folder doesn't exist, try just the mXX folder
                            fallback_path = template_base / month_part / full_filename
                            if fallback_path.exists():
                                self.log_link(clean_line, str(fallback_path))
                            else:
                                self.log(clean_line)
                    else:
                        self.log(clean_line)
                p.wait()
                self.refresh_ui()
            else:
                self.log(f"ERROR: File not found at {final_path}")

        threading.Thread(target=worker, daemon=True).start()

    # --- UI HELPERS AND CONFIGURATION ---

    def setup_main_tab(self):
        status_frame = ttk.LabelFrame(self.main_tab, text=" System Status ", padding="10")
        status_frame.pack(fill="x", padx=15, pady=5)
        row1 = ttk.Frame(status_frame)
        row1.pack(fill="x")
        ttk.Label(row1, text="Client:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.client_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.client_var, foreground="#005fb8",
                  font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 10))
        ttk.Label(row1, text="Website:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.web_status_var = tk.StringVar(value="...")
        ttk.Label(row1, textvariable=self.web_status_var, foreground="#2e86c1",
                  font=('Segoe UI', 9, 'bold')).pack(side="left", padx=(5, 10))
        ttk.Label(row1, text="Indexer:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.indexer_var = tk.StringVar(value="...")
        self.indexer_status_lbl = ttk.Label(
            row1, textvariable=self.indexer_var, font=('Segoe UI', 9, 'bold'))
        self.indexer_status_lbl.pack(side="left", padx=5)
        row2 = ttk.Frame(status_frame)
        row2.pack(fill="x", pady=(8, 0))
        ttk.Label(row2, text="Generation Preset:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        self.preset_var = tk.StringVar(value="...")
        ttk.Label(row2, textvariable=self.preset_var, foreground="#6c3483",
                  font=('Segoe UI', 9, 'bold')).pack(side="left", padx=10)
        conf_frame = ttk.LabelFrame(self.main_tab, text=" Configuration ", padding="10")
        conf_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(conf_frame, text="Client:", font=(
            'Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky="w")
        self.client_combo = ttk.Combobox(
            conf_frame, values=self.get_available_clients(), state="readonly", width=15)
        self.client_combo.grid(row=0, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.client_combo.bind("<<ComboboxSelected>>", self.apply_client_switch)
        ttk.Label(conf_frame, text="Website:", font=('Segoe UI', 9, 'bold')
                  ).grid(row=1, column=0, sticky="w", pady=10)
        self.web_folder_var = tk.StringVar()
        self.web_folder_var.trace_add("write", self.handle_web_change)
        ttk.Entry(conf_frame, textvariable=self.web_folder_var, width=15).grid(
            row=1, column=1, sticky="w", padx=(5, 0), pady=10)
        self.btn_update_web = tk.Button(conf_frame, text="Update Website",
                                        command=self.update_web_folder_in_ares, width=15, relief="raised", bd=1, bg="#f0f0f0")
        self.btn_update_web.grid(row=1, column=2, padx=(5, 0), pady=10)
        ttk.Label(conf_frame, text="Preset:", font=(
            'Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky="w")
        self.preset_combo = ttk.Combobox(conf_frame, values=[
                                         "HTML EN", "HTML GR-EN", "HTML GR-EN / EN", "PDF EN", "PDF GR-EN", "PDF GR"], state="readonly", width=15)
        self.preset_combo.grid(row=2, column=1, columnspan=2, sticky="w", padx=(5, 0))
        self.preset_combo.bind("<<ComboboxSelected>>", self.apply_preset)
        ttk.Label(conf_frame, text="Indexer:", font=('Segoe UI', 9, 'bold')
                  ).grid(row=3, column=0, sticky="w", pady=(10, 0))
        idx_btn_frame = ttk.Frame(conf_frame)
        idx_btn_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=(5, 0), pady=(10, 0))
        self.idx_state = tk.StringVar()
        tk.Radiobutton(idx_btn_frame, text="ON", variable=self.idx_state, value="yes",
                       indicatoron=0, width=5, command=lambda: self.set_indexer("yes")).pack(side="left")
        tk.Radiobutton(idx_btn_frame, text="OFF", variable=self.idx_state, value="no",
                       indicatoron=0, width=5, command=lambda: self.set_indexer("no")).pack(side="left")

    def handle_web_change(self, *args): self.btn_update_web.configure(bg="red" if self.web_folder_var.get() != self.web_status_var.get() else "#f0f0f0", fg="white" if self.web_folder_var.get()
                                                                      != self.web_status_var.get() else "black", font=('Segoe UI', 9, 'bold' if self.web_folder_var.get() != self.web_status_var.get() else 'normal'))

    def refresh_ui(self):
        client = "..."
        if os.path.exists(CONTEXT_FILE):
            with open(CONTEXT_FILE, 'r') as f:
                client = f.read().strip()
                self.client_var.set(client.upper())
                self.client_combo.set(client)
        path = self.find_ares_file(client)
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                idx_match = re.search(r'generate\.services\.index\s*=\s*"([^"]+)"', content)
                if idx_match:
                    val = idx_match.group(1).lower()
                    self.indexer_var.set("ON" if val == "yes" else "OFF")
                    self.idx_state.set(val)
                    self.indexer_status_lbl.configure(foreground="green" if val == "yes" else "red")
                f_match = re.search(
                    r'generated\.website\.folder\.root\s*=\s*"([^/]+)/dcs"', content)
                if f_match:
                    current_val = f_match.group(1)
                    self.web_status_var.set(current_val)
                    self.web_folder_var.set(current_val)
                    self.btn_update_web.configure(bg="#f0f0f0", fg="black")
            except:
                pass
        if os.path.exists(PRESET_STATUS):
            with open(PRESET_STATUS, 'r') as f:
                self.preset_var.set(f.read().strip())

    def find_ares_file(self, client):
        target = f"pref.website_{client}.ares"
        for r, _, files in os.walk(CLIENTS_BASE):
            if target in files:
                return os.path.join(r, target)
        return None

    def get_available_clients(self):
        try:
            return [d for d in os.listdir(CLIENTS_BASE) if os.path.isdir(os.path.join(CLIENTS_BASE, d))]
        except:
            return []

    def apply_client_switch(self, event):
        client = self.client_combo.get()
        with open(CONTEXT_FILE, 'w') as f:
            f.write(client)
        threading.Thread(target=self.sync_master_ares, args=(client,), daemon=True).start()

    def sync_master_ares(self, client_name):
        try:
            with open(MASTER_ARES, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = r'(selected\.pref\.main\s*=\s*"pref\.main_)([^"]+)(")'
            if re.search(pattern, content):
                new_content = re.sub(pattern, rf'\1{client_name}\3', content)
                with open(MASTER_ARES, 'w', encoding='utf-8', newline='') as f:
                    f.write(new_content)
        except Exception as e:
            self.log(f"Error: {e}")
        self.refresh_ui()

    def update_web_folder_in_ares(self):
        client, folder = self.client_combo.get(), self.web_folder_var.get().strip()
        path = self.find_ares_file(client)
        if not path or not folder:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(path, 'w', encoding='utf-8', newline='') as f:
                for line in lines:
                    if "generated.website.folder.root" in line:
                        f.write(f'generated.website.folder.root = "{folder}/dcs"\n')
                    else:
                        f.write(line)
            self.refresh_ui()
            messagebox.showinfo("Updated", f"Website folder set to: {folder}")
        except Exception as e:
            self.log(f"Error: {e}")

    def set_indexer(self, state): self.run_script(INDEXER_SCRIPT, state)

    def apply_preset(self, event):
        sel = self.preset_combo.get()
        mapping = {"HTML EN": "HTML_E", "HTML GR-EN": "HTML_GE", "HTML GR-EN / EN": "HTML_GE_E",
                   "PDF EN": "PDF_E", "PDF GR-EN": "PDF_GE", "PDF GR": "PDF_G"}
        self.run_script(PRESET_SCRIPT, mapping[sel])
        f = open(PRESET_STATUS, 'w')
        f.write(sel)
        f.close()
        self.refresh_ui()

    def toggle_log(self):
        if self.log_frame.winfo_viewable():
            self.log_frame.pack_forget()
            self.btn_log_toggle.configure(text="SHOW LOG")
        else:
            self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
            self.btn_log_toggle.configure(text="HIDE LOG")

    def clear_log(self): self.console.config(state='normal'); self.console.delete(
        '1.0', tk.END); self.console.config(state='disabled')


if __name__ == "__main__":
    tk_root = tk.Tk()
    app = ALWBWorkflowManager(tk_root)
    tk_root.mainloop()