import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import re
from datetime import datetime

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

class ALWB_Demo_App:
    def __init__(self, root):
        self.root = root
        self.root.title("DCS Generation Dashboard (Demo Mode)")
        self.root.geometry("550x850")
        self.style = ttk.Style()
        self.style.theme_use('xpnative')

        # Main Layout
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tabs
        self.setup_what_tab()
        self.setup_who_tab()
        self.setup_when_tab()
        self.setup_post_gen_tab()

        # Activity Log (Bottom)
        self.log_frame = ttk.LabelFrame(self.root, text=" Activity Log ", padding="5")
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.console = scrolledtext.ScrolledText(self.log_frame, height=10, state='disabled', font=('Consolas', 9))
        self.console.pack(fill="both", expand=True)
        
        self.log("System Initialized in Demo Mode.")

    def log(self, msg):
        self.console.config(state='normal')
        self.console.insert(tk.END, f"> {msg}\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def demo_action(self, action_name):
        self.log(f"Action Triggered: {action_name}")
        self.log("Note: This is a standalone demo. External script execution is bypassed.")

    # --- TAB 1: WHAT ---
    def setup_what_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" What ")
        container = ttk.Frame(tab, padding="20")
        container.pack(fill="both", expand=True)
        v_frame = ttk.LabelFrame(container, text=" Template Readiness (What) ", padding="15")
        v_frame.pack(fill="x", pady=10)
        ttk.Label(v_frame, text="Select a month to validate template consistency:").pack(anchor="w")
        combo = ttk.Combobox(v_frame, values=["January", "February", "March"], state="readonly")
        combo.pack(pady=10, fill="x")
        combo.set("January")
        btn = ttk.Button(v_frame, text="Run Validation Report", command=lambda: self.demo_action("Validation Report"))
        btn.pack(pady=5)
        ToolTip(btn, "Compares filename date vs internal Set_Date and reports Status")

    # --- TAB 2: WHO ---
    def setup_who_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Who - Where - How ")
        status_frame = ttk.LabelFrame(tab, text=" System Status ", padding="10")
        status_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(status_frame, text="Client: GOA", font=('Segoe UI', 9, 'bold'), foreground="#005fb8").pack(side="left", padx=5)
        
        conf_frame = ttk.LabelFrame(tab, text=" Configuration ", padding="10")
        conf_frame.pack(fill="x", padx=15, pady=5)
        ttk.Label(conf_frame, text="Client:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(conf_frame, values=["goa", "monastery", "chapel"], width=15).grid(row=0, column=1, padx=5)
        
        btn = tk.Button(conf_frame, text="Update Website", bg="#f0f0f0", relief="raised", bd=1)
        btn.grid(row=1, column=0, columnspan=2, pady=10)
        ToolTip(btn, "Update the website folder root for this client")

    # --- TAB 3: WHEN ---
    def setup_when_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" When ")
        container = ttk.Frame(tab, padding="10")
        container.pack(fill="both", expand=True)
        
        r_frame = ttk.LabelFrame(container, text=" Final Regex (Review or Edit) ", padding="10")
        r_frame.pack(fill="x", pady=5)
        ent = ttk.Entry(r_frame, font=('Consolas', 10))
        ent.insert(0, "se.m(01|02).d(..).(..|...)")
        ent.pack(side="left", fill="x", expand=True, padx=5)
        
        btn = tk.Button(r_frame, text="Update", bg="#f0f0f0", relief="raised", bd=1)
        btn.pack(side="left")
        ToolTip(btn, "Update generator.atem with these settings")

    # --- TAB 4: POST-GENERATION ---
    def setup_post_gen_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=" Post-Generation ")
        container = ttk.Frame(tab, padding="10")
        container.pack(fill="both", expand=True)

        # Utilities Section
        util_frame = ttk.LabelFrame(container, text=" Post-Generation Utilities ", padding="10")
        util_frame.pack(fill="x", pady=(0, 5))
        
        row = ttk.Frame(util_frame); row.pack(fill="x")
        ttk.Label(row, text="PDF:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        b1 = ttk.Button(row, text="Add Logo", command=lambda: self.demo_action("Add Logo"), width=9)
        b1.pack(side="left", padx=5)
        ToolTip(b1, "Add GOA logo to PDF covers")
        
        ttk.Label(row, text="HTML:", font=('Segoe UI', 9, 'bold')).pack(side="left")
        b2 = ttk.Button(row, text="Insert Code", command=lambda: self.demo_action("Insert Google Analytics"), width=10)
        b2.pack(side="left", padx=5)
        ToolTip(b2, "Insert google analytics code into HTML files")

        # Index Editor Section
        editor_frame = ttk.LabelFrame(container, text=" Index Editor ", padding="10")
        editor_frame.pack(fill="both", expand=True, pady=5)
        
        sel_row = ttk.Frame(editor_frame); sel_row.pack(fill="x")
        ttk.Combobox(sel_row, values=["goa"], width=8).pack(side="left", padx=2)
        ttk.Button(sel_row, text="Load", width=8, command=lambda: self.log("Index Loaded (Demo)")).pack(side="left", padx=5)
        
        txt = tk.Text(editor_frame, height=10, font=('Consolas', 10))
        txt.insert("1.0", "Sunday of the Publican and Pharisee\nPresentation of Our Lord\nSunday of the Prodigal Son")
        txt.pack(fill="both", expand=True, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ALWB_Demo_App(root)
    root.mainloop()