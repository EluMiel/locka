import tkinter as tk

class Application(tk.Frame):
    def __init__(self, root):
        super().__init__(root, width=420, height=320, borderwidth=4, relief="groove")
        self.pack()
        self.pack_propagate(0)
        self.root = root
        self.create_widgets()

    def create_widgets(self):
        self.listbnox = tk.Listbox(self, width=50, height=15, selectmode="browse")
        self.listbnox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Example items
        self.listbnox.insert(tk.END, "Google | testuser | password123")
        self.listbnox.insert(tk.END, "Facebook | testuser | password123")
    
root=tk.Tk()
root.title("Locka")
root.geometry("800x600")

app=Application(root=root)
app.mainloop()