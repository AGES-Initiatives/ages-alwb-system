import os
import tkinter as tk
from tkinter import ttk

# --- PATHS ---
from path_settings import CONTEXT_FILE, BASE_DIR

def get_clients_and_active():
    """Scans the b-preferences folder for client directories."""
    if not os.path.exists(BASE_DIR):
        return [], ""
    clients = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    active = ""
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
            active = f.read().strip()
    return sorted(clients), active

class ClientSwitcherApp:
    def __init__(self, root, clients, active):
        self.root = root
        # If launched as Toplevel, it won't have its own title/geometry unless set
        self.root.title("Set Generation Client")
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Select Client Context:", font=('Segoe UI', 10)).pack()
        
        self.client_var = tk.StringVar(value=active)
        self.combo = ttk.Combobox(main_frame, textvariable=self.client_var, values=clients, state="readonly", width=40)
        self.combo.pack(pady=15)
        
        ttk.Button(main_frame, text="SET CLIENT & SYNC", command=self.save_selection).pack()

    def save_selection(self):
        selection = self.client_var.get()
        if selection:
            with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
                f.write(selection)
        # destroy() closes this window but leaves the Dashboard (parent) running
        self.root.destroy()

if __name__ == "__main__":
    # Standard standalone launch logic
    root = tk.Tk()
    clients, active = get_current_clients_and_active()
    app = ClientSwitcherApp(root, clients, active)
    root.mainloop()