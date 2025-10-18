import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List with Category, Date & Time")
        self.root.minsize(450, 580)
        self.root.config(bg="#f8fafc")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        title = tk.Label(
            root,
            text="🗂️ To-Do List",
            font=("Helvetica", 20, "bold"),
            bg="#f8fafc",
            fg="#111827"
        )
        title.grid(row=0, column=0, pady=(15, 5))

        input_frame = tk.Frame(root, bg="#f8fafc")
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        input_frame.columnconfigure(0, weight=1)

        self.task_entry = tk.Entry(
            input_frame,
            font=("Helvetica", 14),
            relief="solid",
            bd=1
        )
        self.task_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=5)

        self.category_var = tk.StringVar()
        categories = ["Work", "Personal", "Study", "Shopping", "Other"]
        self.category_menu = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=10,
            font=("Helvetica", 12)
        )
        self.category_menu.set("Select...")
        self.category_menu.grid(row=0, column=1, padx=(0, 10))

        add_btn = tk.Button(
            input_frame,
            text="➕ Add Task",
            command=self.add_task,
            bg="#22c55e",
            activebackground="#16a34a",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            height=1
        )
        add_btn.grid(row=0, column=2, ipadx=10)

        task_container = tk.Frame(root, bg="#f8fafc")
        task_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)

        self.canvas = tk.Canvas(task_container, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(task_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.task_list_frame = tk.Frame(self.canvas, bg="#f8fafc")
        self.canvas.create_window((0, 0), window=self.task_list_frame, anchor="nw")

        self.task_list_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.tasks = []

        clear_btn = tk.Button(
            root,
            text="🗑️ Clear All",
            command=self.clear_tasks,
            bg="#ef4444",
            activebackground="#dc2626",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            pady=6
        )
        clear_btn.grid(row=3, column=0, sticky="ew", padx=40, pady=15)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        category = self.category_var.get()

        if not task_text:
            messagebox.showwarning("Warning", "Please enter a task!")
            return
        if category == "Select...":
            messagebox.showwarning("Warning", "Please select a category!")
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")

        frame = tk.Frame(self.task_list_frame, bg="#ffffff", padx=5, pady=6, relief="solid", bd=1)
        frame.pack(fill="x", padx=5, pady=5, expand=True)

        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame, variable=var, bg="#ffffff", activebackground="#ffffff")
        checkbox.pack(side="left", padx=5)

        text_frame = tk.Frame(frame, bg="#ffffff")
        text_frame.pack(side="left", fill="x", expand=True)

        label = tk.Label(
            text_frame,
            text=task_text,
            font=("Helvetica", 13),
            bg="#ffffff",
            anchor="w",
            wraplength=300
        )
        label.pack(anchor="w")

        info_label = tk.Label(
            text_frame,
            text=f"🏷️ {category}   |   📅 {date_str}   🕒 {time_str}",
            font=("Helvetica", 10, "italic"),
            fg="#6b7280",
            bg="#ffffff"
        )
        info_label.pack(anchor="w")

        del_btn = tk.Button(
            frame,
            text="❌",
            command=lambda f=frame: self.delete_task(f),
            bg="#fca5a5",
            activebackground="#f87171",
            relief="flat",
            width=3
        )
        del_btn.pack(side="right", padx=5)

        self.tasks.append((frame, var, label, info_label))
        self.task_entry.delete(0, tk.END)
        self.category_menu.set("Select...")

    def delete_task(self, frame):
        frame.destroy()
        self.tasks = [t for t in self.tasks if t[0] != frame]

    def clear_tasks(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all tasks?"):
            for frame, *_ in self.tasks:
                frame.destroy()
            self.tasks.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
