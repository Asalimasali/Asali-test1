import json
import os
import csv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import defaultdict

plt.rcParams['font.family'] = 'Segoe UI'

DATA_FILE = "transactions.json"
DEFAULT_CATEGORIES = ["Salary", "Groceries", "Transport", "Entertainment", "Utilities", "Other"]

class PersonalWalletAdvancedApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💰 Personal Wallet - Advanced Edition")
        self.geometry("1200x800")
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
        style.configure("Stats.TButton", background="#4CAF50", foreground="white")
        style.map("Stats.TButton", background=[('active', '#45A049')])

        self.transactions = []
        self.categories = list(DEFAULT_CATEGORIES)
        self.budget_limits = {}
        self.current_month_filter = datetime.now().strftime("%Y-%m")

        self._build_ui()
        self._load_data()
        self._refresh_ui()

    def _build_ui(self):
        # --- Title ---
        title_label = ttk.Label(self, text="📘 Personal Wallet - Advanced Edition", font=("Segoe UI", 16, 'bold'), anchor='center')
        title_label.pack(pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tab 1: Transactions
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="💳 Transactions")

        # Tab 2: Analytics
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="📊 Analytics")

        # Tab 3: Budget
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="💰 Budget")

        self._build_transactions_tab()
        self._build_analytics_tab()
        self._build_budget_tab()

    def _build_transactions_tab(self):
        container = ttk.Frame(self.tab1, padding=15)
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

        # --- Search and Filter Frame ---
        filter_frame = ttk.Labelframe(container, text="Search & Filter", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._refresh_ui)
        ttk.Entry(filter_frame, textvariable=self.search_var, width=20).grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.filter_category_var = tk.StringVar(value="All")
        categories_all = ["All"] + self.categories
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, 
                                                values=categories_all, state="readonly", width=15)
        self.filter_category_combo.grid(row=0, column=3, padx=5)
        self.filter_category_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_ui())

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=4, sticky=tk.W, padx=(10,0))
        self.filter_type_var = tk.StringVar(value="All")
        ttk.Combobox(filter_frame, textvariable=self.filter_type_var, 
                    values=["All", "Income", "Expense"], state="readonly", width=12).grid(row=0, column=5, padx=5)
        self.filter_type_var.trace('w', lambda *args: self._refresh_ui())

        ttk.Label(filter_frame, text="Month:").grid(row=0, column=6, sticky=tk.W, padx=(10,0))
        self.month_var = tk.StringVar(value=self.current_month_filter)
        month_entry = ttk.Entry(filter_frame, textvariable=self.month_var, width=10)
        month_entry.grid(row=0, column=7, padx=5)
        self.month_var.trace('w', lambda *args: self._refresh_ui())

        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).grid(row=0, column=8, padx=10)

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

        self.stats_var = tk.StringVar(value="Income: 0.00 | Expenses: 0.00")
        stats_label = tk.Label(bot, textvariable=self.stats_var, font=("Segoe UI", 10), bg="#F6F8FA")
        stats_label.pack(side=tk.LEFT, padx=20)

        ttk.Button(bot, text="🗑️ Delete Selected", command=self.delete_selected, style="Delete.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(bot, text="📤 Export CSV", command=self.export_csv, style="Export.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(bot, text="📥 Import JSON", command=self.import_json, style="Import.TButton").pack(side=tk.RIGHT, padx=4)

    def _build_analytics_tab(self):
        container = ttk.Frame(self.tab2, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Statistics Frame
        stats_frame = ttk.Labelframe(container, text="Financial Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0,10))

        self.stats_text = tk.Text(stats_frame, height=8, font=("Segoe UI", 9))
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Charts Frame
        charts_frame = ttk.Frame(container)
        charts_frame.pack(fill=tk.BOTH, expand=True)

        # Pie Chart
        pie_frame = ttk.Labelframe(charts_frame, text="Expense Categories Distribution", padding=10)
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        self.pie_figure = Figure(figsize=(6, 4), dpi=100)
        self.pie_canvas = FigureCanvasTkAgg(self.pie_figure, pie_frame)
        self.pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Monthly Trend
        trend_frame = ttk.Labelframe(charts_frame, text="Monthly Income vs Expenses", padding=10)
        trend_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))

        self.trend_figure = Figure(figsize=(6, 4), dpi=100)
        self.trend_canvas = FigureCanvasTkAgg(self.trend_figure, trend_frame)
        self.trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_budget_tab(self):
        container = ttk.Frame(self.tab3, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Budget Setup Frame
        setup_frame = ttk.Labelframe(container, text="Set Monthly Budget", padding=10)
        setup_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(setup_frame, text="Category:").grid(row=0, column=0, sticky=tk.W)
        self.budget_category_var = tk.StringVar()
        self.budget_category_combo = ttk.Combobox(setup_frame, textvariable=self.budget_category_var, 
                                                values=self.categories, state="readonly", width=15)
        self.budget_category_combo.grid(row=0, column=1, padx=5)
        if self.categories:
            self.budget_category_combo.set(self.categories[0])

        ttk.Label(setup_frame, text="Monthly Limit:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        self.budget_amount_var = tk.StringVar()
        ttk.Entry(setup_frame, textvariable=self.budget_amount_var, width=15).grid(row=0, column=3, padx=5)

        ttk.Button(setup_frame, text="Set Budget", command=self.set_budget, style="Add.TButton").grid(row=0, column=4, padx=5)

        # Budget Overview
        overview_frame = ttk.Labelframe(container, text="Budget Overview", padding=10)
        overview_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("category", "budget", "spent", "remaining", "status")
        self.budget_tree = ttk.Treeview(overview_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.budget_tree.heading(col, text=col.capitalize())
            self.budget_tree.column(col, anchor=tk.CENTER)
        self.budget_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        self.budget_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Alerts Frame
        self.alerts_frame = ttk.Labelframe(container, text="Budget Alerts", padding=10)
        self.alerts_frame.pack(fill=tk.X, pady=(10,0))

        self.alerts_text = tk.Text(self.alerts_frame, height=4, font=("Segoe UI", 9), bg="#FFF3CD")
        self.alerts_text.pack(fill=tk.BOTH, expand=True)

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
        self.filter_category_combo['values'] = ["All"] + self.categories
        self.budget_category_combo['values'] = self.categories
        self.category_combo.set(name)
        self.new_cat_var.set("")
        self._save_data()

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
            self.filter_category_combo['values'] = ["All"] + self.categories
            self.budget_category_combo['values'] = self.categories
            if self.categories:
                self.category_combo.set(self.categories[0])
            messagebox.showinfo("Removed", f"Category '{cur}' removed.")
            self._save_data()

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
                    self.filter_category_combo['values'] = ["All"] + self.categories
                    self.budget_category_combo['values'] = self.categories
                self.budget_limits = payload.get('budget_limits', {})
            except Exception as e:
                messagebox.showwarning("Load Error", f"Failed to load data file: {e}")
                self.transactions = []
        else:
            self.transactions = []

    def _save_data(self):
        payload = {
            'transactions': self.transactions, 
            'categories': self.categories, 
            'budget_limits': self.budget_limits,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    # --- Filter Functions ---
    def clear_filters(self):
        self.search_var.set("")
        self.filter_category_var.set("All")
        self.filter_type_var.set("All")
        self.month_var.set(self.current_month_filter)
        self._refresh_ui()

    def _filter_transactions(self):
        filtered = self.transactions.copy()
        
        # Search filter
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [tx for tx in filtered if 
                       search_term in tx.get('description', '').lower() or 
                       search_term in tx.get('category', '').lower()]
        
        # Category filter
        category_filter = self.filter_category_var.get()
        if category_filter != "All":
            filtered = [tx for tx in filtered if tx.get('category') == category_filter]
        
        # Type filter
        type_filter = self.filter_type_var.get()
        if type_filter != "All":
            filtered = [tx for tx in filtered if tx.get('type') == type_filter]
        
        # Month filter
        month_filter = self.month_var.get()
        if month_filter:
            filtered = [tx for tx in filtered if tx.get('date', '').startswith(month_filter)]
        
        return filtered

    # --- UI Refresh ---
    def _refresh_ui(self):
        # Refresh transactions tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        filtered_transactions = self._filter_transactions()
        for tx in filtered_transactions:
            self.tree.insert('', tk.END, values=(
                tx['id'], tx['date'], tx['type'], tx['category'], 
                f"{tx['amount']:.2f}", tx.get('description','')
            ))

        # Calculate and display balance and statistics
        total_income = sum(float(tx['amount']) for tx in self.transactions if tx['type'] == 'Income')
        total_expenses = sum(float(tx['amount']) for tx in self.transactions if tx['type'] == 'Expense')
        balance = total_income - total_expenses
        
        color = "#2E8B57" if balance >= 0 else "#B22222"
        self.balance_var.set(f"Balance: {balance:.2f}")
        self.balance_label.configure(fg=color)
        self.stats_var.set(f"Income: {total_income:.2f} | Expenses: {total_expenses:.2f}")

        # Refresh analytics
        self._update_analytics()
        
        # Refresh budget
        self._update_budget_display()

    def _update_analytics(self):
        # Update statistics text
        self.stats_text.delete(1.0, tk.END)
        
        current_month = datetime.now().strftime("%Y-%m")
        month_income = sum(float(tx['amount']) for tx in self.transactions 
                          if tx['type'] == 'Income' and tx['date'].startswith(current_month))
        month_expenses = sum(float(tx['amount']) for tx in self.transactions 
                            if tx['type'] == 'Expense' and tx['date'].startswith(current_month))
        
        stats_text = f"""
Financial Overview:
-------------------
Total Balance: {sum(float(tx['amount']) if tx['type']=='Income' else -float(tx['amount']) for tx in self.transactions):.2f}
Total Income: {sum(float(tx['amount']) for tx in self.transactions if tx['type'] == 'Income'):.2f}
Total Expenses: {sum(float(tx['amount']) for tx in self.transactions if tx['type'] == 'Expense'):.2f}

Current Month ({current_month}):
-------------------------------
Monthly Income: {month_income:.2f}
Monthly Expenses: {month_expenses:.2f}
Monthly Savings: {month_income - month_expenses:.2f}

Transaction Count:
------------------
Total Transactions: {len(self.transactions)}
Income Transactions: {len([tx for tx in self.transactions if tx['type'] == 'Income'])}
Expense Transactions: {len([tx for tx in self.transactions if tx['type'] == 'Expense'])}
"""
        self.stats_text.insert(1.0, stats_text)

        # Update pie chart
        self._update_pie_chart()
        
        # Update trend chart
        self._update_trend_chart()

    def _update_pie_chart(self):
        self.pie_figure.clear()
        ax = self.pie_figure.add_subplot(111)
        
        # Get expense data by category
        expense_data = defaultdict(float)
        for tx in self.transactions:
            if tx['type'] == 'Expense':
                expense_data[tx['category']] += float(tx['amount'])
        
        if expense_data:
            categories = list(expense_data.keys())
            amounts = list(expense_data.values())
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.set_title('Expense Distribution by Category')
            
            # Style the chart
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'No expense data\navailable', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Expense Distribution by Category')
        
        self.pie_canvas.draw()

    def _update_trend_chart(self):
        self.trend_figure.clear()
        ax = self.trend_figure.add_subplot(111)
        
        # Group by month
        monthly_data = defaultdict(lambda: {'income': 0, 'expenses': 0})
        for tx in self.transactions:
            month = tx['date'][:7]  # YYYY-MM
            amount = float(tx['amount'])
            if tx['type'] == 'Income':
                monthly_data[month]['income'] += amount
            else:
                monthly_data[month]['expenses'] += amount
        
        if monthly_data:
            months = sorted(monthly_data.keys())
            income = [monthly_data[month]['income'] for month in months]
            expenses = [monthly_data[month]['expenses'] for month in months]
            
            x = range(len(months))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], income, width, label='Income', color='#2E8B57')
            ax.bar([i + width/2 for i in x], expenses, width, label='Expenses', color='#B22222')
            
            ax.set_xlabel('Month')
            ax.set_ylabel('Amount')
            ax.set_title('Monthly Income vs Expenses')
            ax.set_xticks(x)
            ax.set_xticklabels(months, rotation=45)
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Monthly Income vs Expenses')
        
        self.trend_figure.tight_layout()
        self.trend_canvas.draw()

    def _update_budget_display(self):
        # Clear existing items
        for i in self.budget_tree.get_children():
            self.budget_tree.delete(i)
        
        # Clear alerts
        self.alerts_text.delete(1.0, tk.END)
        
        current_month = datetime.now().strftime("%Y-%m")
        alerts = []
        
        for category, budget_limit in self.budget_limits.items():
            # Calculate spent this month
            spent = sum(float(tx['amount']) for tx in self.transactions 
                       if tx['category'] == category and tx['type'] == 'Expense' 
                       and tx['date'].startswith(current_month))
            
            remaining = float(budget_limit) - spent
            status = "Within Budget" if remaining >= 0 else "Over Budget"
            
            # Add to treeview
            self.budget_tree.insert('', tk.END, values=(
                category, f"{float(budget_limit):.2f}", f"{spent:.2f}", 
                f"{remaining:.2f}", status
            ))
            
            # Generate alerts
            if remaining < 0:
                alerts.append(f"⚠️ OVER BUDGET: {category} exceeded by {-remaining:.2f}")
            elif remaining < float(budget_limit) * 0.2:  # Less than 20% remaining
                alerts.append(f"🔔 WARNING: {category} has only {remaining:.2f} remaining")
        
        if not alerts:
            alerts.append("✅ All budgets are within limits")
        
        self.alerts_text.insert(1.0, "\n".join(alerts))

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
        if not sel: 
            messagebox.showinfo("Info", "No transaction selected.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected transaction(s)?"): 
            return
        ids_to_delete = [int(self.tree.item(s)['values'][0]) for s in sel]
        self.transactions = [tx for tx in self.transactions if tx['id'] not in ids_to_delete]
        self._save_data()
        self._refresh_ui()

    # --- Budget Functions ---
    def set_budget(self):
        category = self.budget_category_var.get()
        if not category:
            messagebox.showwarning("Validation", "Please select a category.")
            return
        
        amount_str = self.budget_amount_var.get().strip()
        if not amount_str:
            messagebox.showwarning("Validation", "Please enter a budget amount.")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0: raise ValueError
        except:
            messagebox.showwarning("Validation", "Please enter a valid positive number for budget.")
            return
        
        self.budget_limits[category] = amount
        self._save_data()
        self._update_budget_display()
        self.budget_amount_var.set("")
        messagebox.showinfo("Success", f"Budget for {category} set to {amount:.2f}")

    # --- Export/Import Functions ---
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', 
                                          filetypes=[('CSV files','*.csv')], 
                                          title='Export transactions to CSV')
        if not path: 
            return
        
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount', 'Description'])
                for tx in self.transactions:
                    writer.writerow([
                        tx['id'], tx['date'], tx['type'], tx['category'],
                        f"{tx['amount']:.2f}", tx.get('description', '')
                    ])
            messagebox.showinfo("Exported", f"Data exported to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[('JSON files','*.json'),('All Files','*.*')], 
                                        title='Import transactions')
        if not path: 
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f: 
                payload = json.load(f)
            imported = payload.get('transactions', [])
            if not isinstance(imported, list): 
                raise ValueError('Invalid format')
            
            next_id = self._next_id()
            for tx in imported:
                try: 
                    amt = float(tx.get('amount', 0))
                except: 
                    amt = 0.0
                new_tx = {
                    'id': next_id, 
                    'date': tx.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'type': tx.get('type','Expense'), 
                    'category': tx.get('category','Other'),
                    'amount': round(amt,2), 
                    'description': tx.get('description','')
                }
                self.transactions.append(new_tx)
                next_id += 1
            
            file_cats = payload.get('categories')
            if isinstance(file_cats, list):
                for c in file_cats:
                    if c not in self.categories: 
                        self.categories.append(c)
                self.category_combo['values'] = self.categories
                self.filter_category_combo['values'] = ["All"] + self.categories
                self.budget_category_combo['values'] = self.categories
            
            # Import budgets if available
            file_budgets = payload.get('budget_limits', {})
            if file_budgets:
                self.budget_limits.update(file_budgets)
            
            self._save_data()
            self._refresh_ui()
            messagebox.showinfo("Imported", f"Imported {len(imported)} transactions from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")

if __name__ == '__main__':
    app = PersonalWalletAdvancedApp()
    app.mainloop()