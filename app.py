import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
from pathlib import Path
from datetime import datetime
import os
from security import encrypt_items, decrypt_items

class Application(tk.Frame):
    MASK = "********"  # パスワード非表示設定時の表示文字列
    
    def __init__(self, root=None, master_password: str = ""):
        super().__init__(root)
        self.root = root
        self.master_password = master_password
        
        # ウィンドウサイズ設定
        self.root.geometry("600x300")
        self.root.minsize(600, 300)

        self.pack(fill="both", expand=True)

        # ttkテーマ
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.BG = "#F4F9FC"  # 白～薄いマリンブルーベース
        self.BORDER = "#C7DCE8"  # 淡いブルー（枠線）
        self.TEXT = "#0B2E3A"  # ディープネイビー
        self.ACCENT = "#1B7AA6"  # マリンブルー（ホバー時）
        self.MINT = "#A8D3E6"  # ライトブルー（デフォルト）

        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("TSeparator", background=self.BORDER)

        style.configure("TButton", padding=(12,6))
        style.map("TButton",
            background=[("active", self.ACCENT), ("!active", self.MINT)],
            foreground=[("active", self.TEXT), ("!active", self.TEXT)]
        )
        
        # クリアボタン用のカスタムスタイル
        style.configure("Clear.TButton", padding=(12,6))
        style.map("Clear.TButton",
            background=[("active", self.BORDER), ("!active", self.BG)],
            foreground=[("active", self.TEXT), ("!active", self.TEXT)]
        )
        
        # スクロールバーのスタイル
        style.configure("Vertical.TScrollbar", background=self.MINT, troughcolor=self.BG, bordercolor=self.BORDER, lightcolor=self.MINT, darkcolor=self.ACCENT)
        style.map("Vertical.TScrollbar",
            background=[("active", self.ACCENT), ("!active", self.MINT)]
        )
        
        # チェックボタンのスタイル
        style.configure("TCheckbutton", background=self.BG, foreground=self.TEXT)
        style.map("TCheckbutton",
            background=[("active", self.BORDER), ("!active", self.BG)],
            foreground=[("active", self.TEXT), ("!active", self.TEXT)]
        )
        
        # フォント統一
        self.root.option_add("*Font", ("Segoe UI", 10))

        self.items: list[dict[str, str]] = []
        self.search_var = tk.StringVar(value="")
        self.search_var.trace_add("write", lambda *_: self.refresh_listbox())
        self.show_pw = tk.BooleanVar(value=True)  # パスワード表示/非表示の切り替え用
        
        self.create_widgets()
        self.load_items()
        self.refresh_listbox()

    def create_widgets(self):
    # ===== 全体レイアウト（上/中/下） =====
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    # ---- 上：検索バー ----
        top_frame = ttk.Frame(self, padding=(10, 10, 10, 5))
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)  # 左の空きを伸ばして右寄せにする

        ttk.Label(top_frame, text="").grid(row=0, column=0, sticky="ew")  # 伸びるダミー（右寄せ用）
        ttk.Label(top_frame, text="検索:").grid(row=0, column=1, padx=(0, 6))

        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=28)
        self.search_entry.grid(row=0, column=2)

        clear_btn = ttk.Button(top_frame, text="×", command=self.clear_search, width=3, style="Clear.TButton")
        clear_btn.grid(row=0, column=3, padx=(6, 0))

    # 区切り線
        ttk.Separator(self, orient="horizontal").grid(row=1, column=0, sticky="ew")

    # ---- 中：リスト ----
        list_frame = ttk.Frame(self, padding=(10, 10, 10, 10))
        list_frame.grid(row=2, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
    # ListboxはtkのままでOK（ttkに相当がない）
        self.listbox = tk.Listbox(list_frame,yscrollcommand=scrollbar.set,activestyle="none",height=12,background=self.BG,foreground=self.TEXT,selectbackground=self.ACCENT,selectforeground=self.BG,borderwidth=1,relief="solid",bd=1)
        self.listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.listbox.yview)

    # ---- 下：操作ボタン群 ----
        btn_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        btn_frame.grid(row=3, column=0, sticky="ew")
        btn_frame.grid_columnconfigure(10, weight=1)  # 右側のチェックを右寄せする

    # ボタンサイズ統一（幅を揃えると一気に“整ってる感”出る）
        btn_w = 10
        ttk.Button(btn_frame, text="追加", command=self.add_item, width=btn_w).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(btn_frame, text="削除", command=self.delete_item, width=btn_w).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(btn_frame, text="IDコピー", command=self.copy_id, width=btn_w).grid(row=0, column=2, padx=(0, 6))
        ttk.Button(btn_frame, text="PWコピー", command=self.copy_pw, width=btn_w).grid(row=0, column=3, padx=(0, 6))
        ttk.Button(btn_frame, text="編集", command=self.edit_item, width=btn_w).grid(row=0, column=4, padx=(0, 6))

        ttk.Checkbutton(btn_frame,text="パスワード表示",variable=self.show_pw,command=self.on_toggle_show_pw).grid(row=0, column=11, sticky="e")    

    def delete_item(self):
        selected=self.listbox.curselection()
        if not selected:
            return
        
        index=selected[0]
        del self.items[index]
        self.commit_change("削除")
        

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
        self.commit_change("追加")

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
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        path = data_dir / "locka.enc"

        payload = {"items": self.items,"settings": {"show_pw": self.show_pw.get()},}

        blob = encrypt_items(payload, master_password=self.master_password)

        with path.open("wb") as f:
            f.write(blob)
        
    def load_items(self):
        path = Path("data") / "locka.enc"
        if not path.exists():
            self.items = []
            self.show_pw.set(True)
            return
        blob = path.read_bytes()
        try:
            payload = decrypt_items(blob, master_password=self.master_password)
        except ValueError as e:
            messagebox.showerror("復号エラー", str(e))
            self.items = []
            self.show_pw.set(True)
            return
        # payload形式の安全策
        if isinstance(payload, dict):
            self.items = payload.get("items", []) or []
            settings = payload.get("settings", {}) or {}
            self.show_pw.set(bool(settings.get("show_pw", True)))
        else:
            # 旧形式（listだけ保存してた場合）への保険
            self.items = payload if isinstance(payload, list) else []
            self.show_pw.set(True)
            
    def format_item(self, item: dict[str, str]) -> str:
        pw_text = item['pw'] if self.show_pw.get() else self.MASK
        return f"{item['site']} | ID: {item['id']} | PW: {pw_text}"
    
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        
        keyword = self.search_var.get().strip().lower()
        
        for item in self.items:
            # 検索対象フィルタリング
            haystack = item.get("site", "").lower()
            if keyword and keyword not in haystack:
                continue
            self.listbox.insert(tk.END, self.format_item(item))

    def on_toggle_show_pw(self):
        self.refresh_listbox()
        self.commit_change("パスワード表示切り替え")
                
    def write_unsaved_backup(self, payload: dict) -> Path:
        """保存に失敗した際、現在のメモリ上の状態をバックアップに保存する。"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = data_dir / f"locka_unsaved_{ts}.json"
        
        with backup_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            
        return backup_path
    
    def commit_change(self, action_label: str):
        """
        変更後に保存を試みる。
        失敗した場合:
            - unsavedバックアップ作成
            - エラー通知
            - JSONからデータを読み直してロールバック
        """
        payload = {
            "items": self.items,
            "settings": {"show_pw": self.show_pw.get()}
        }
        
        try:
            # 自動保存なのでメッセージは出さない
            self.save_items()
            
        except Exception as e:
            # 失敗した状態を退避
            try:
                backup_path = self.write_unsaved_backup(payload)
                backup_msg = f"\nバックアップファイル: {backup_path}"
            except Exception:
                backup_msg = "\nバックアップファイルの作成に失敗しました。"
                
            messagebox.showerror(
                "保存エラー",
                f"{action_label}後の保存に失敗しました。\n"
                "最後に保存された状態にロールバックします。"
                f"{backup_msg}\n\n"
                f"エラー詳細: {e}"
            )
            
            self.load_items()

        finally:
            self.refresh_listbox()
            
    def edit_item(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        current = self.items[index]
        
        # 既存値を初期値にして入力させる(Cancelで中断)
        site = simpledialog.askstring("編集", "サイト名を入力してください。", initialvalue=current["site"], parent=self.root)
        if site is None:
            return
        
        user_id = simpledialog.askstring("編集", "IDを入力してください。", initialvalue=current["id"], parent=self.root)
        if user_id is None:
            return
        
        pw = simpledialog.askstring("編集", "パスワードを入力してください。", initialvalue=current["pw"], parent=self.root)
        if pw is None:
            return
        
        # 同じ行を上書き
        self.items[index] = {"site": site, "id": user_id, "pw": pw}
        self.refresh_listbox()
        self.commit_change("編集")
        
    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus_set()


def prompt_master_password(root: tk.Tk) -> str | None:
    """
    既存encがあれば「復号できるパス」を求める。
    なければ「新規パス作成（2回確認）」を行う。
    """
    enc_path = Path("data") / "locka.enc"
    root.withdraw()  # 先にメイン窓を隠す

    if enc_path.exists():
        # 既存データ → 正しいパスが入るまでループ（キャンセルで終了）
        while True:
            pw = simpledialog.askstring(
                "Locka 認証",
                "マスターパスワードを入力してください。",
                show="*",
                parent=root,
            )
            if pw is None:
                return None

            try:
                blob = enc_path.read_bytes()
                decrypt_items(blob, master_password=pw)  # 復号できるかチェック
                return pw
            except Exception:
                messagebox.showerror("認証エラー", "パスワードが異なるか、データが壊れています。")
    else:
        # 初回 → 新規作成（2回入力）
        while True:
            pw1 = simpledialog.askstring(
                "Locka",
                "新しいマスターパスワードを設定してください。",
                show="*",
                parent=root,
            )
            if pw1 is None:
                return None
            if pw1.strip() == "":
                messagebox.showwarning("入力エラー", "空のパスワードは設定できません。")
                continue
            pw2 = simpledialog.askstring(
                "Locka",
                "確認のためもう一度入力してください。",
                show="*",
                parent=root,
            )
            if pw2 is None:
                return None
            if pw1 != pw2:
                messagebox.showerror("確認エラー", "パスワードが一致しません。もう一度設定してください。")
                continue
            return pw1


root = tk.Tk()
root.title("Locka")
root.geometry("800x600")

master = prompt_master_password(root)
if master is None:
    root.destroy()
    raise SystemExit

app = Application(root, master_password=master)

root.deiconify()   # 認証できたら表示
root.mainloop()
