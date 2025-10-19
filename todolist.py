import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import tkinter.font as tkfont

class ModernToDo:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Modern To-Do Manager v2")
        self.root.geometry("1000x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f9fafb")

        self.tasks = []
        self._id_counter = 1

        self.font_main = tkfont.Font(family="Segoe UI", size=11)
        self.font_bold = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.font_title = tkfont.Font(family="Segoe UI", size=18, weight="bold")

        self._build_ui()

    def _build_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg="#ffffff", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="🗂️  Modern To-Do Manager", font=self.font_title, bg="#ffffff", fg="#1e293b").pack()

        # NEW TASK AREA
        new_frame = tk.Frame(self.root, bg="#f9fafb", pady=10)
        new_frame.pack(fill="x", padx=20)

        tk.Label(new_frame, text="Task:", bg="#f9fafb", font=self.font_bold).grid(row=0, column=0, sticky="w")
        self.task_var = tk.StringVar()
        tk.Entry(new_frame, textvariable=self.task_var, width=45, font=self.font_main, relief="solid", bd=1).grid(row=0, column=1, padx=(5,15))

        tk.Label(new_frame, text="Category:", bg="#f9fafb", font=self.font_bold).grid(row=0, column=2, sticky="w")
        self.cat_var = tk.StringVar(value="General")
        cat_box = ttk.Combobox(new_frame, textvariable=self.cat_var, values=["General","Work","Personal","Study","Home","Shopping"], width=12, state="readonly")
        cat_box.grid(row=0, column=3, padx=(5,15))

        tk.Label(new_frame, text="Priority:", bg="#f9fafb", font=self.font_bold).grid(row=0, column=4, sticky="w")
        self.prio_var = tk.StringVar(value="Medium")
        prio_box = ttk.Combobox(new_frame, textvariable=self.prio_var, values=["Low","Medium","High"], width=10, state="readonly")
        prio_box.grid(row=0, column=5, padx=(5,15))

        add_btn = tk.Button(new_frame, text="➕ Add", bg="#22c55e", fg="white", relief="flat",
                            font=self.font_bold, command=self._add_task)
        add_btn.grid(row=0, column=6, ipadx=8, padx=(10,0))

        # FILTER AREA
        filter_frame = tk.Frame(self.root, bg="#ffffff", pady=10)
        filter_frame.pack(fill="x", padx=20, pady=(5,5))

        tk.Label(filter_frame, text="🔍 Search:", bg="#ffffff").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        search_box = tk.Entry(filter_frame, textvariable=self.search_var, width=30, relief="solid", bd=1)
        search_box.grid(row=0, column=1, padx=(6,20))
        search_box.bind("<KeyRelease>", lambda e: self._refresh_view())

        tk.Label(filter_frame, text="Category:", bg="#ffffff").grid(row=0, column=2)
        self.filter_cat = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_cat, values=["All","General","Work","Personal","Study","Home","Shopping"],
                     width=12, state="readonly").grid(row=0, column=3, padx=(6,20))
        self.filter_cat.trace_add("write", lambda *a: self._refresh_view())

        tk.Label(filter_frame, text="Status:", bg="#ffffff").grid(row=0, column=4)
        self.filter_status = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_status, values=["All","Pending","Done"],
                     width=10, state="readonly").grid(row=0, column=5, padx=(6,0))
        self.filter_status.trace_add("write", lambda *a: self._refresh_view())

        # TABLE
        table_frame = tk.Frame(self.root, bg="#f9fafb")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(5,5))

        cols = ("status","priority","category","task","created")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col, w in zip(cols, [90,90,120,500,160]):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")

        self.tree.tag_configure("done", foreground="#6b7280", font=("Segoe UI", 10, "overstrike"))
        self.tree.tag_configure("pending", foreground="#111827", font=("Segoe UI", 10))

        # BUTTONS
        btn_frame = tk.Frame(self.root, bg="#f9fafb", pady=8)
        btn_frame.pack(fill="x", padx=20)

        def make_btn(text, color, cmd):
            return tk.Button(btn_frame, text=text, bg=color, fg="white", relief="flat",
                            font=self.font_main, activebackground=color, command=cmd)

        make_btn("✅ Toggle", "#3b82f6", self._toggle_done).pack(side="left", padx=6)
        make_btn("✏️ Edit", "#f59e0b", self._edit_task).pack(side="left", padx=6)
        make_btn("🗑️ Delete", "#ef4444", self._delete_task).pack(side="left", padx=6)
        make_btn("🧹 Delete All", "#dc2626", self._delete_all).pack(side="left", padx=6)  
        make_btn("📊 Stats", "#8b5cf6", self._show_stats).pack(side="left", padx=6)
        make_btn("🔄 Refresh", "#10b981", self._refresh_view).pack(side="right", padx=6)


        # STATS
        stats_frame = tk.Frame(self.root, bg="#ffffff", pady=12)
        stats_frame.pack(fill="x", padx=20, pady=(8,12))
        self.stats_label = tk.Label(stats_frame, text="", bg="#ffffff", fg="#374151", font=self.font_bold)
        self.stats_label.pack(anchor="center")

        # double click edit
        self.tree.bind("<Double-1>", lambda e: self._edit_task())

    # ========== LOGIC ==========
    def _add_task(self):
        text = self.task_var.get().strip()
        if not text:
            messagebox.showwarning("Empty", "Please enter a task.")
            return
        item = {
            "id": self._id_counter,
            "task": text,
            "category": self.cat_var.get(),
            "priority": self.prio_var.get(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "done": False
        }
        self._id_counter += 1
        self.tasks.append(item)
        self.task_var.set("")
        self._refresh_view()

    def _refresh_view(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = self.search_var.get().lower().strip()
        cat = self.filter_cat.get()
        status = self.filter_status.get()

        for t in self.tasks:
            if query and query not in t["task"].lower():
                continue
            if cat != "All" and t["category"] != cat:
                continue
            if status == "Pending" and t["done"]:
                continue
            if status == "Done" and not t["done"]:
                continue

            st = "✅ Done" if t["done"] else "⏳ Pending"
            tag = "done" if t["done"] else "pending"
            self.tree.insert("", "end", iid=f"t-{t['id']}",
                             values=(st, t["priority"], t["category"], t["task"], t["created"]),
                             tags=(tag,))
        self._update_stats()

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a task first.")
            return None
        tid = int(sel[0].split("-")[1])
        for t in self.tasks:
            if t["id"] == tid:
                return t
        return None

    def _toggle_done(self):
        t = self._get_selected()
        if not t: return
        t["done"] = not t["done"]
        self._refresh_view()

    def _edit_task(self):
        t = self._get_selected()
        if not t: return
        new_text = simpledialog.askstring("Edit Task", "Task:", initialvalue=t["task"])
        if not new_text: return
        new_cat = simpledialog.askstring("Edit Category", "Category:", initialvalue=t["category"]) or t["category"]
        new_prio = simpledialog.askstring("Edit Priority", "Priority (Low/Medium/High):", initialvalue=t["priority"]) or t["priority"]
        t["task"], t["category"], t["priority"] = new_text.strip(), new_cat.strip(), new_prio.strip().capitalize()
        self._refresh_view()

    def _delete_task(self):
        t = self._get_selected()
        if not t: return
        if messagebox.askyesno("Delete", "Delete selected task?"):
            self.tasks = [x for x in self.tasks if x["id"] != t["id"]]
            self._refresh_view()

    def _delete_all(self):
        if not self.tasks:
            messagebox.showinfo("Info", "No tasks to delete.")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to delete ALL tasks?"):
            self.tasks.clear()
            self._refresh_view()
            messagebox.showinfo("Deleted", "All tasks have been deleted.")


    def _show_stats(self):
        total = len(self.tasks)
        done = sum(t["done"] for t in self.tasks)
        messagebox.showinfo("Stats", f"Total: {total}\nCompleted: {done}\nPending: {total-done}")

    def _update_stats(self):
        total = len(self.tasks)
        done = sum(t["done"] for t in self.tasks)
        pending = total - done
        self.stats_label.config(text=f"Tasks: {total}   |   ✅ Completed: {done}   |   ⏳ Pending: {pending}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernToDo(root)
    root.mainloop()
