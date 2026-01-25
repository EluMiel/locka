import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import json
from pathlib import Path

class Application(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=420, height=320, borderwidth=4, relief="groove")
        self.pack()
        self.pack_propagate(False)
        self.root = root
        self.items=[]
        self.create_widgets()
        self.load_items()
        self.refresh_listbox()

    def create_widgets(self): #self.itemsとListboxの同期はインデックスで管理する。(並び順の挙動に注意。)
        self.listbox = tk.Listbox(self, width=50, height=15, selectmode="browse")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        add_btn = tk.Button(self)
        add_btn["text"] = "追加"
        add_btn["command"] = self.add_item
        add_btn.pack(side="left", padx=5, pady=5)
        
        delete_btn = tk.Button(self)
        delete_btn["text"] = "削除"
        delete_btn["command"] = self.delete_item
        delete_btn.pack(side="left", padx=5, pady=5)
        
        copy_id_btn = tk.Button(self)
        copy_id_btn["text"] = "IDコピー"
        copy_id_btn["command"] = self.copy_id
        copy_id_btn.pack(side="left", padx=5, pady=5)

        copy_pw_btn = tk.Button(self)
        copy_pw_btn["text"] = "PWコピー"
        copy_pw_btn["command"] = self.copy_pw
        copy_pw_btn.pack(side="left", padx=5, pady=5)
        
        save_btn = tk.Button(self)
        save_btn["text"] = "保存"
        save_btn["command"] = self.save_items
        save_btn.pack(side="left", padx=5, pady=5)
    
    def delete_item(self):
        selected=self.listbox.curselection()
        if not selected:
            return
        index=selected[0]
        del self.items[index]
        self.refresh_listbox()

    def add_item(self):
        site = simpledialog.askstring("追加", "サイト名を入力してください:", parent=self.root)
        if site is None:
            return
        user_id = simpledialog.askstring("追加", "IDを入力してください:", parent=self.root)
        if user_id is None:
            return
        pw = simpledialog.askstring("追加", "パスワードを入力してください:", parent=self.root)
        if pw is None:
            return

        item = {"site": site, "id": user_id, "pw": pw}
        self.items.append(item)
        self.refresh_listbox()

    def copy_id(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        user_id = self.items[index]['id']

        self.root.clipboard_clear()
        self.root.clipboard_append(user_id)
        self.root.update()

    def copy_pw(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        pw = self.items[index]['pw']

        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        self.root.update()

    def save_items(self):
        # 保存先 (プロジェクト直下の data/locka.json)
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        path = data_dir / "locka.json"
        
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
            
        self.show_saved_message()
        
    def show_saved_message(self):
        messagebox.showinfo("保存", "保存しました。")
        
    def load_items(self):
        path = Path("data") / "locka.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                self.items = json.load(f)
        else:
            self.items = []
            
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, f"{item['site']} | {item['id']} | {item['pw']}")
        
root=tk.Tk()
root.title("Locka")
root.geometry("800x600")

app=Application(root)
app.mainloop()