import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATA_FILE = "transactions.json"
DEFAULT_CATEGORIES = ["Salary", "Groceries", "Transport", "Entertainment", "Utilities", "Other"]

class PersonalWalletApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💰 Personal Wallet - Color Enhanced")
        self.geometry("900x600")
        self.configure(bg="#F6F8FA")

        # --- Style Setup ---
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", background="#F6F8FA", font=("Segoe UI", 10))
        style.configure("TFrame", background="#F6F8FA")
        style.configure("TButton", font=("Segoe UI", 10, 'bold'), padding=6, relief="flat")
        style.configure("Treeview", font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, 'bold'), background="#E5E9F0")
        style.map("Treeview", background=[('selected', '#CCE5FF')])

        # --- Colored Button Styles ---
        style.configure("Add.TButton", background="#2C7BE5", foreground="white")
        style.map("Add.TButton", background=[('active', '#1E6AD7')])
        style.configure("Delete.TButton", background="#E53935", foreground="white")
        style.map("Delete.TButton", background=[('active', '#C62828')])
        style.configure("Import.TButton", background="#FF9800", foreground="white")
        style.map("Import.TButton", background=[('active', '#FB8C00')])
        style.configure("Export.TButton", background="#9C27B0", foreground="white")
        style.map("Export.TButton", background=[('active', '#7B1FA2')])

        self.transactions = []
        self.categories = list(DEFAULT_CATEGORIES)

        self._build_ui()
        self._load_data()
        self._refresh_ui()

    def _build_ui(self):
        # --- Title ---
        title_label = ttk.Label(self, text="📘 Personal Wallet", font=("Segoe UI", 16, 'bold'), anchor='center')
        title_label.pack(pady=10)

        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # --- Input Frame ---
        top = ttk.Labelframe(container, text="Add Transaction", padding=15)
        top.pack(fill=tk.X, pady=(0,10))

        ttk.Label(top, text="Amount:").grid(row=0, column=0, sticky=tk.W)
        self.amount_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.amount_var, width=15).grid(row=0, column=1, padx=5)

        ttk.Label(top, text="Type:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.type_var = tk.StringVar(value="Expense")
        ttk.OptionMenu(top, self.type_var, "Expense", "Expense", "Income").grid(row=0, column=3)

        ttk.Label(top, text="Category:").grid(row=0, column=4, sticky=tk.W, padx=(10,0))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(top, textvariable=self.category_var, values=self.categories, state="readonly", width=18)
        self.category_combo.grid(row=0, column=5)
        self.category_combo.set(self.categories[0])

        ttk.Label(top, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=(8,0))
        self.desc_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.desc_var, width=40).grid(row=1, column=1, columnspan=3, pady=(8,0))

        ttk.Label(top, text="Date (YYYY-MM-DD):").grid(row=1, column=4, sticky=tk.W, pady=(8,0))
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(top, textvariable=self.date_var, width=14).grid(row=1, column=5, pady=(8,0))

        add_btn = ttk.Button(top, text="➕ Add", command=self.add_transaction, style="Add.TButton")
        add_btn.grid(row=0, column=6, rowspan=2, padx=(15,0), sticky=tk.N+tk.S+tk.E+tk.W)

        # --- Category Frame ---
        cat_frame = ttk.Labelframe(container, text="Manage Categories", padding=10)
        cat_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Label(cat_frame, text="Add Category:").grid(row=0, column=0, sticky=tk.W)
        self.new_cat_var = tk.StringVar()
        ttk.Entry(cat_frame, textvariable=self.new_cat_var, width=20).grid(row=0, column=1, padx=5)
        ttk.Button(cat_frame, text="Add", command=self.add_category, style="Add.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(cat_frame, text="Remove Selected", command=self.remove_selected_category, style="Delete.TButton").grid(row=0, column=3, padx=5)

        # --- Transaction History ---
        mid = ttk.Labelframe(container, text="Transaction History", padding=10)
        mid.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "type", "category", "amount", "description")
        self.tree = ttk.Treeview(mid, columns=columns, show="headings", height=12)
        for c in columns:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, anchor=tk.CENTER)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Bottom Section ---
        bot = ttk.Frame(container, padding=10)
        bot.pack(fill=tk.X)
        self.balance_var = tk.StringVar(value="Balance: 0.00")
        self.balance_label = tk.Label(bot, textvariable=self.balance_var, font=("Segoe UI", 12, 'bold'), fg="#2E8B57", bg="#F6F8FA")
        self.balance_label.pack(side=tk.LEFT)

        ttk.Button(bot, text="🗑️ Delete Selected", command=self.delete_selected, style="Delete.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(bot, text="📤 Export JSON", command=self.export_json, style="Export.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(bot, text="📥 Import JSON", command=self.import_json, style="Import.TButton").pack(side=tk.RIGHT, padx=4)

    # --- Category Functions ---
    def add_category(self):
        name = self.new_cat_var.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Category name can't be empty.")
            return
        if name in self.categories:
            messagebox.showinfo("Info", "Category already exists.")
            return
        self.categories.append(name)
        self.category_combo['values'] = self.categories
        self.category_combo.set(name)
        self.new_cat_var.set("")

    def remove_selected_category(self):
        cur = self.category_combo.get()
        if not cur:
            messagebox.showinfo("Info", "No category selected.")
            return
        if cur in DEFAULT_CATEGORIES:
            messagebox.showwarning("Protected", "Default categories cannot be removed.")
            return
        if cur in self.categories:
            self.categories.remove(cur)
            self.category_combo['values'] = self.categories
            if self.categories:
                self.category_combo.set(self.categories[0])
            messagebox.showinfo("Removed", f"Category '{cur}' removed.")

    # --- Data Load/Save ---
    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    payload = json.load(f)
                self.transactions = payload.get('transactions', [])
                file_cats = payload.get('categories')
                if isinstance(file_cats, list):
                    for c in file_cats:
                        if c not in self.categories:
                            self.categories.append(c)
                    self.category_combo['values'] = self.categories
            except Exception as e:
                messagebox.showwarning("Load Error", f"Failed to load data file: {e}")
                self.transactions = []
        else:
            self.transactions = []

    def _save_data(self):
        payload = {'transactions': self.transactions, 'categories': self.categories, 'last_updated': datetime.now().isoformat()}
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    # --- UI Refresh ---
    def _refresh_ui(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for tx in self.transactions:
            self.tree.insert('', tk.END, values=(tx['id'], tx['date'], tx['type'], tx['category'], f"{tx['amount']:.2f}", tx.get('description','')))
        balance = sum(float(tx['amount']) if tx['type']=='Income' else -float(tx['amount']) for tx in self.transactions)
        color = "#2E8B57" if balance >= 0 else "#B22222"
        self.balance_var.set(f"Balance: {balance:.2f}")
        self.balance_label.configure(fg=color)

    # --- Transaction Functions ---
    def _next_id(self):
        if not self.transactions:
            return 1
        return max(tx['id'] for tx in self.transactions) + 1

    def add_transaction(self):
        amt_str = self.amount_var.get().strip()
        if not amt_str:
            messagebox.showwarning("Validation", "Amount is required.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0: raise ValueError
        except:
            messagebox.showwarning("Validation", "Please enter a valid positive number for amount.")
            return
        tx_type = self.type_var.get()
        category = self.category_var.get() or 'Other'
        desc = self.desc_var.get().strip()
        date_str = self.date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showwarning("Validation", "Date must be in YYYY-MM-DD format.")
            return
        tx = {'id': self._next_id(), 'date': date_str, 'type': tx_type, 'category': category,
              'amount': round(amt,2), 'description': desc}
        self.transactions.append(tx)
        self._save_data()
        self._refresh_ui()
        self.amount_var.set("")
        self.desc_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("Info", "No transaction selected."); return
        if not messagebox.askyesno("Confirm", "Delete selected transaction(s)?"): return
        ids_to_delete = [int(self.tree.item(s)['values'][0]) for s in sel]
        self.transactions = [tx for tx in self.transactions if tx['id'] not in ids_to_delete]
        self._save_data()
        self._refresh_ui()

    def export_json(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')], title='Export transactions')
        if not path: return
        payload = {'transactions': self.transactions, 'categories': self.categories, 'exported_at': datetime.now().isoformat()}
        try:
            with open(path, 'w', encoding='utf-8') as f: json.dump(payload, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Exported", f"Data exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[('JSON files','*.json'),('All Files','*.*')], title='Import transactions')
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f: payload = json.load(f)
            imported = payload.get('transactions', [])
            if not isinstance(imported, list): raise ValueError('Invalid format')
            next_id = self._next_id()
            for tx in imported:
                try: amt = float(tx.get('amount', 0))
                except: amt = 0.0
                new_tx = {'id': next_id, 'date': tx.get('date', datetime.now().strftime('%Y-%m-%d')),
                          'type': tx.get('type','Expense'), 'category': tx.get('category','Other'),
                          'amount': round(amt,2), 'description': tx.get('description','')}
                self.transactions.append(new_tx)
                next_id += 1
            file_cats = payload.get('categories')
            if isinstance(file_cats, list):
                for c in file_cats:
                    if c not in self.categories: self.categories.append(c)
                self.category_combo['values'] = self.categories
            self._save_data()
            self._refresh_ui()
            messagebox.showinfo("Imported", f"Imported {len(imported)} transactions from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")

if __name__ == '__main__':
    app = PersonalWalletApp()
    app.mainloop()
