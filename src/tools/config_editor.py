import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import src.dna.config as config

class ConfigEditor(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("⚙️ 設定 (Settings)")
        self.geometry("450x600")
        self.config(bg="black")
        
        # --- Data Prep ---
        self.vars = {} # {key: tk.Variable}
        self.initial_types = {} # {key: type}
        
        # --- UI Layout ---
        self.mainframe = tk.Frame(self, bg="black")
        self.mainframe.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.mainframe, bg="black", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.mainframe, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="black")
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Populate
        self._load_configs()
        
        # Buttons
        btn_frame = tk.Frame(self, bg="black")
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="保存 (Save)", command=self._save, bg="#444", fg="white", font=("MS Gothic", 10)).pack(side="left", padx=20, expand=True)
        tk.Button(btn_frame, text="リセット (Reset)", command=self._reset, bg="#822", fg="white", font=("MS Gothic", 10)).pack(side="right", padx=20, expand=True)
        
        # Mouse Wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _load_configs(self):
        row = 0
        
        # Filter Logic
        items = []
        for key in dir(config):
            if key.startswith("_"): continue
            # Exclude imports and system paths
            if key in ["os", "json", "load_dotenv", "BASE_DIR", "MEMORY_DIR", "TEMP_DIR", "USER_CONFIG_PATH", "load_user_config", "threading", "Enum", "auto", "Dict", "Tuple"]: continue
            
            val = getattr(config, key)
            if callable(val): continue
            if isinstance(val, (type, threading.Lock.__class__)): continue
            if str(type(val)) == "<class 'module'>": continue
            
            items.append((key, val))
            
        # Sort: Booleans first (User Request), then others (alphabetical)
        items.sort(key=lambda x: (not isinstance(x[1], bool), x[0]))

        for key, val in items:
            self.initial_types[key] = type(val)
            
            # Row Container
            frame = tk.Frame(self.scroll_frame, bg="black")
            frame.pack(fill="x", padx=10, pady=2)
            
            # Label
            lbl = tk.Label(frame, text=key, fg="#aaa", bg="black", width=30, anchor="w", font=("Consolas", 9))
            lbl.pack(side="left")
            
            # Input
            if isinstance(val, bool):
                var = tk.BooleanVar(value=val)
                cb = tk.Checkbutton(frame, variable=var, bg="black", activebackground="black", selectcolor="#444")
                cb.pack(side="left")
                self.vars[key] = var
            elif isinstance(val, (int, float)):
                # Use Entry for numbers
                var = tk.DoubleVar(value=val) if isinstance(val, float) else tk.IntVar(value=val)
                entry = tk.Entry(frame, textvariable=var, bg="#222", fg="white", insertbackground="white", width=20)
                entry.pack(side="left", fill="x", expand=True)
                self.vars[key] = var
            else:
                try:
                    # Generic String fallback (list/dict/str)
                    var = tk.StringVar(value=str(val))
                    entry = tk.Entry(frame, textvariable=var, bg="#222", fg="white", insertbackground="white", width=20)
                    entry.pack(side="left", fill="x", expand=True)
                    self.vars[key] = var
                except:
                    # Cannot serialize
                    pass

    def _save(self):
        updates = {}
        error_list = []
        
        for key, var in self.vars.items():
            try:
                val = var.get()
                updates[key] = val
            except Exception as e:
                error_list.append(f"{key}: {e}")
        
        if error_list:
             messagebox.showerror("Validation Error", "\n".join(error_list))
             return

        try:
            with open(config.USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(updates, f, indent=2)
            messagebox.showinfo("Saved", "設定を保存しました。\n反映するには再起動してください。\nPlease restart to apply changes.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _reset(self):
        if messagebox.askyesno("Reset", "設定をリセットしますか？\n(All settings will be restored to defaults on restart)"):
            if os.path.exists(config.USER_CONFIG_PATH):
                try:
                    os.remove(config.USER_CONFIG_PATH)
                    messagebox.showinfo("Reset", "リセットしました。再起動してください。")
                    self.destroy()
                except Exception as e:
                     messagebox.showerror("Error", str(e))
            else:
                messagebox.showinfo("Info", "変更された設定はありません。")
