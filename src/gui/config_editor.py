import json
import os
import tkinter as tk
from tkinter import messagebox

CONFIG_FILE = "config/config.json"

class ConfigEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Config Editor")
        self.geometry("600x450")
        
        self.config_data = {"accounts": []}
        self.current_index = -1
        
        self.load_config()
        self.create_widgets()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
        if "accounts" not in self.config_data:
            self.config_data["accounts"] = []

    def create_widgets(self):
        # Left frame: List of accounts
        left_frame = tk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(left_frame, text="Accounts").pack()
        
        self.listbox = tk.Listbox(left_frame, width=20)
        self.listbox.pack(fill=tk.Y, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Add", command=self.add_account).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Delete", command=self.delete_account).pack(side=tk.RIGHT, expand=True, fill=tk.X)
        
        # Right frame: Account details
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(self.right_frame, text="Account Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.var_name = tk.StringVar()
        self.entry_name = tk.Entry(self.right_frame, textvariable=self.var_name, width=40)
        self.entry_name.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.var_name.trace_add("write", self.update_listbox_name)
        
        tk.Label(self.right_frame, text="Token:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.var_token = tk.StringVar()
        tk.Entry(self.right_frame, textvariable=self.var_token, width=40).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        tk.Label(self.right_frame, text="Target Bot ID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.var_bot_id = tk.StringVar()
        tk.Entry(self.right_frame, textvariable=self.var_bot_id, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        tk.Label(self.right_frame, text="Channel ID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.var_channel_id = tk.StringVar()
        tk.Entry(self.right_frame, textvariable=self.var_channel_id, width=40).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Commands frame
        cmd_frame = tk.LabelFrame(self.right_frame, text="Commands")
        cmd_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=10)
        
        self.cmd_vars = {
            "claim": tk.BooleanVar(),
            "daily": tk.BooleanVar(),
            "weekly": tk.BooleanVar(),
            "wage": tk.BooleanVar(),
            "club_wage": tk.BooleanVar(),
            "arena-match": tk.BooleanVar()
        }
        
        for i, (cmd, var) in enumerate(self.cmd_vars.items()):
            tk.Checkbutton(cmd_frame, text=cmd, variable=var).grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            
        tk.Button(self.right_frame, text="Save Settings", command=self.save_config, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)
        
        self.refresh_listbox()
        if self.config_data["accounts"]:
            self.listbox.selection_set(0)
            self.on_select(None)
            
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for acc in self.config_data["accounts"]:
            self.listbox.insert(tk.END, acc.get("account_name", "Unknown"))
            
    def update_listbox_name(self, *args):
        if self.current_index >= 0 and self.current_index < self.listbox.size():
            name = self.var_name.get()
            self.listbox.delete(self.current_index)
            self.listbox.insert(self.current_index, name)
            self.listbox.selection_set(self.current_index)
            
    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
            
        self.save_current_to_dict()
        
        self.current_index = selection[0]
        acc = self.config_data["accounts"][self.current_index]
        
        self.var_name.set(acc.get("account_name", ""))
        self.var_token.set(acc.get("token", ""))
        self.var_bot_id.set(str(acc.get("target_bot_id", "")))
        self.var_channel_id.set(str(acc.get("channel_id", "")))
        
        cmds = acc.get("commands", {})
        for cmd, var in self.cmd_vars.items():
            var.set(cmds.get(cmd, False))
            
    def save_current_to_dict(self):
        if self.current_index >= 0 and self.current_index < len(self.config_data["accounts"]):
            acc = self.config_data["accounts"][self.current_index]
            acc["account_name"] = self.var_name.get()
            acc["token"] = self.var_token.get()
            
            try:
                acc["target_bot_id"] = int(self.var_bot_id.get()) if self.var_bot_id.get() else ""
            except ValueError:
                acc["target_bot_id"] = self.var_bot_id.get()
                
            try:
                acc["channel_id"] = int(self.var_channel_id.get()) if self.var_channel_id.get() else ""
            except ValueError:
                acc["channel_id"] = self.var_channel_id.get()
                
            if "commands" not in acc:
                acc["commands"] = {}
            for cmd, var in self.cmd_vars.items():
                acc["commands"][cmd] = var.get()

    def add_account(self):
        self.save_current_to_dict()
        new_acc = {
            "account_name": "New_Account",
            "token": "",
            "target_bot_id": "",
            "channel_id": "",
            "commands": {
                "claim": True,
                "daily": True,
                "weekly": True,
                "wage": True,
                "club_wage": False,
                "arena-match": True
            }
        }
        self.config_data["accounts"].append(new_acc)
        self.refresh_listbox()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.on_select(None)
        
    def delete_account(self):
        if self.current_index >= 0:
            if messagebox.askyesno("Confirm", "Delete this account?"):
                del self.config_data["accounts"][self.current_index]
                self.current_index = -1
                self.refresh_listbox()
                
                self.var_name.set("")
                self.var_token.set("")
                self.var_bot_id.set("")
                self.var_channel_id.set("")
                for var in self.cmd_vars.values():
                    var.set(False)
                    
                if self.config_data["accounts"]:
                    self.listbox.selection_set(0)
                    self.on_select(None)
                    
    def save_config(self):
        self.save_current_to_dict()
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

if __name__ == "__main__":
    app = ConfigEditor()
    app.mainloop()
