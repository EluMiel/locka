import tkinter as tk

class Application(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=420, height=320, borderwidth=4, relief="groove")
        self.pack()
        self.pack_propagate(False)
        self.root = root
        self.items=[
            {"site":"Google", "id":"testuser", "pw":"password123"},
            {"site":"Facebook", "id":"testuser", "pw":"password123"},
        ]
        self.create_widgets()

    def create_widgets(self):
        self.listbox = tk.Listbox(self, width=50, height=15, selectmode="browse")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for item in self.items:
            self.listbox.insert(tk.END, f"{item['site']} | {item['id']} | {item['pw']}")
        add_btn = tk.Button(self)
        add_btn["text"] = "追加"
        add_btn["command"] = lambda: print("Add button clicked")
        add_btn.pack(side="left", padx=5, pady=5)
        
        delete_btn = tk.Button(self)
        delete_btn["text"] = "削除"
        delete_btn["command"] = self.delete_item
        delete_btn.pack(side="left", padx=5, pady=5)
        
        id_copy_btn = tk.Button(self)
        id_copy_btn["text"] = "IDコピー"
        id_copy_btn["command"] = lambda: print("ID Copy button clicked")
        id_copy_btn.pack(side="left", padx=5, pady=5)
        
        pw_copy_btn = tk.Button(self)
        pw_copy_btn["text"] = "PWコピー"
        pw_copy_btn["command"] = lambda: print("PW Copy button clicked")
        pw_copy_btn.pack(side="left", padx=5, pady=5)
        
        save_btn = tk.Button(self)
        save_btn["text"] = "保存"
        save_btn["command"] = lambda: print("Save button clicked")
        save_btn.pack(side="left", padx=5, pady=5)
    
    def delete_item(self):
        selected=self.listbox.curselection()
        if not selected:
            return
        index=selected[0]
        del self.items[index]
        self.listbox.delete(index)

root=tk.Tk()
root.title("Locka")
root.geometry("800x600")

app=Application(root)
app.mainloop()