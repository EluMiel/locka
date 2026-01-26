import tkinter as tk
from tkinter import simpledialog, messagebox
import json
from pathlib import Path

class Application(tk.Frame):
    MASK = "********"  # パスワード非表示設定時の表示文字列
    
    def __init__(self, root=None):
        super().__init__(root, width=800, height=600)
        self.pack()
        self.pack_propagate(False)
        self.root = root
        self.items: list[dict[str, str]] = []
        self.show_pw = tk.BooleanVar(value=True)  # パスワード表示/非表示の切り替え用
        self.create_widgets()
        self.load_items()
        self.refresh_listbox()

    def create_widgets(self):  #self.itemsとListboxの同期はインデックスで管理する。(並び順の挙動に注意。)
        # Listbox+Scrollbar用のFrame
        list_frame = tk.Frame(self)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        scrolbar = tk.Scrollbar(list_frame)
        scrolbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrolbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scrolbar.config(command=self.listbox.yview)
        
        # ボタン用のFrame
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5, fill="x")
        
        add_btn = tk.Button(btn_frame, text="追加", command=self.add_item)
        add_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(btn_frame, text="削除", command=self.delete_item)
        delete_btn.pack(side="left", padx=5)
        
        copy_id_btn = tk.Button(btn_frame, text="IDコピー", command=self.copy_id)
        copy_id_btn.pack(side="left", padx=5)

        copy_pw_btn = tk.Button(btn_frame, text="PWコピー", command=self.copy_pw)
        copy_pw_btn.pack(side="left", padx=5)
        
        save_btn = tk.Button(btn_frame, text="保存", command=self.save_items)
        save_btn.pack(side="left", padx=5)
        
        show_pw_cb = tk.Checkbutton(btn_frame, text="パスワード表示", variable=self.show_pw, command=self.on_toggle_show_pw)
        show_pw_cb.pack(side="right", padx=5)

    def delete_item(self):
        selected=self.listbox.curselection()
        if not selected:
            return
        
        index=selected[0]
        del self.items[index]
        
        self.refresh_listbox()
        self.save_items()

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
        self.save_items()

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

    def save_items(self, show_message: bool = True):
        # 保存先 (プロジェクト直下の data/locka.json)
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        path = data_dir / "locka.json"
        
        payload = {
            "items": self.items,
            "settings": {
                "show_pw": self.show_pw.get()
            }
        }
        
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        
        if show_message:  #　保存完了メッセージの表示/非表示切り替え
            self.show_saved_message()
        
    def show_saved_message(self):
        messagebox.showinfo("保存", "保存しました。")
        
    def load_items(self):
        path = Path("data") / "locka.json"
        if not path.exists():
            self.items = []
            return
        
        try:
            with path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("エラー", "JSONファイルが読み込めないため、空のリストで起動します。")
            self.items = []
            return
        
        # 旧型式の取り込み: itemsだけの配列だった場合
        if isinstance(payload, list):
            self.items = payload
            return
        
        # 新型式の取り込み: settings付き
        self.items = payload.get("items", [])
        settings = payload.get("settings", {})
        self.show_pw.set(settings.get("show_pw", True))  # show_pwがない場合はデフォルトをTrueとする。
            
    def format_item(self, item: dict[str, str]) -> str:
        pw_text = item['pw'] if self.show_pw.get() else self.MASK
        return f"{item['site']} | ID: {item['id']} | PW: {pw_text}"
    
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.items:
            self.listbox.insert(tk.END, self.format_item(item))

    def on_toggle_show_pw(self):
        self.refresh_listbox()
        self.save_items(show_message=False)
                
root=tk.Tk()
root.title("Locka")
root.geometry("800x600")

app=Application(root)
app.mainloop()