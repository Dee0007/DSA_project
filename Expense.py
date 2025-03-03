from tkinter import *
from tkinter import messagebox, ttk
import datetime
import sqlite3
import csv
import matplotlib.pyplot as plt

class ExpenseTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Expense Tracker")
        self.master.geometry("900x750")
        self.master.config(bg="#1E1E1E")  # Dark theme
        
        # Database Setup
        self.conn = sqlite3.connect("expenses.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses 
                               (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, amount REAL)''')
        self.conn.commit()
        
        self.expense_visible = False
        
        # UI Elements
        self.create_ui()
    
    def create_ui(self):
        Label(self.master, text="Expense Tracker", font=("Arial", 24, "bold"), bg="#1E1E1E", fg="#FFFFFF").pack(pady=10)
        
        # Input Frame
        self.input_frame = Frame(self.master, bg="#252526", padx=15, pady=15, relief=RIDGE, bd=2)
        self.input_frame.pack(pady=10, padx=20, fill=X)
        
        # Date, Category, Amount aligned horizontally
        ttk.Label(self.input_frame, text="Date:", background="#252526", foreground="#FFFFFF").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.date_entry = ttk.Entry(self.input_frame, font=("Arial", 12), width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)
        self.date_entry.insert(0, datetime.datetime.today().strftime("%d-%m-%Y"))
        
        ttk.Label(self.input_frame, text="Category:", background="#252526", foreground="#FFFFFF").grid(row=0, column=2, padx=10, pady=5, sticky=W)
        self.category_entry = ttk.Combobox(self.input_frame, values=["Food", "Transport", "Shopping", "Bills", "Other"], font=("Arial", 12), width=15)
        self.category_entry.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(self.input_frame, text="Amount (₹):", background="#252526", foreground="#FFFFFF").grid(row=0, column=4, padx=10, pady=5, sticky=W)
        self.amount_entry = ttk.Entry(self.input_frame, font=("Arial", 12), width=15)
        self.amount_entry.grid(row=0, column=5, padx=10, pady=5)
        
        # Buttons Frame
        self.buttons_frame = Frame(self.master, bg="#1E1E1E")
        self.buttons_frame.pack(pady=10)
        
        ttk.Button(self.buttons_frame, text="➕ Add", command=self.add_expense).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(self.buttons_frame, text="🔍 Search", command=self.search_expense).grid(row=0, column=1, padx=10, pady=5)
        
        self.filter_category = ttk.Combobox(self.buttons_frame, values=["All", "Food", "Transport", "Shopping", "Bills", "Other"], font=("Arial", 12), width=10)
        self.filter_category.grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(self.buttons_frame, text="🔎 Filter", command=self.filter_expense).grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Button(self.buttons_frame, text="🗑 Delete", command=self.delete_expense).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(self.buttons_frame, text="📂 Export CSV", command=self.export_to_csv).grid(row=0, column=5, padx=10, pady=5)
        
        ttk.Label(self.buttons_frame, text="From:", background="#1E1E1E", foreground="#FFFFFF").grid(row=1, column=0, padx=10, pady=5)
        self.from_date = ttk.Entry(self.buttons_frame, font=("Arial", 12), width=12)
        self.from_date.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.buttons_frame, text="To:", background="#1E1E1E", foreground="#FFFFFF").grid(row=1, column=2, padx=10, pady=5)
        self.to_date = ttk.Entry(self.buttons_frame, font=("Arial", 12), width=12)
        self.to_date.grid(row=1, column=3, padx=10, pady=5)
        
        ttk.Button(self.buttons_frame, text="📅 Date Filter", command=self.date_filter).grid(row=1, column=4, padx=10, pady=5)
        ttk.Button(self.buttons_frame, text="📊 Analytics", command=self.show_analytics).grid(row=1, column=5, padx=10, pady=5)
        
        # Expense List (Initially Hidden)
        self.expense_frame = Frame(self.master, bg="#252526", padx=10, pady=10, relief=RIDGE, bd=2)
        
        self.tree = ttk.Treeview(self.expense_frame, columns=("ID", "Date", "Category", "Amount"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.pack(fill=BOTH, expand=True)
        
        self.show_button = ttk.Button(self.master, text="📜 Show Expenses", command=self.toggle_expense_list)
        self.show_button.pack(pady=10)
        
        self.show_expenses()
    
    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()
        
        if not date or not category or not amount:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        self.cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
        self.conn.commit()
        
        self.cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (f"%{date[-7:]}",))
        total_spent = self.cursor.fetchone()[0] or 0

        if total_spent > 10000:
            messagebox.showwarning("Warning", f"Total expenses this month: ₹{total_spent}. Consider saving!")


        self.tree.insert("", "end", values=(self.cursor.lastrowid, date, category, amount))  # Add new row to TreeView
        messagebox.showinfo("Success", "Expense added successfully!")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Delete", "Please select a record to delete.")
            return

        confirm = messagebox.askyesno("Delete", "Are you sure you want to delete this expense?")
        if not confirm:
            return
        
        for item in selected_item:
            expense_id = self.tree.item(item, "values")[0]  # Get ID of selected record
            self.cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            self.conn.commit()
            self.tree.delete(item)  # Remove from TreeView

            messagebox.showinfo("Success", "Expense deleted successfully!")

    
    def export_to_csv(self):
        with open("expenses.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Category", "Amount"])
            self.cursor.execute("SELECT * FROM expenses")
            writer.writerows(self.cursor.fetchall())
        messagebox.showinfo("Export", "Expenses exported successfully to expenses.csv!") 

    def date_filter(self):
        from_date = self.from_date.get()
        to_date = self.to_date.get()
        
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ?", (from_date, to_date))
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)
    
    def show_analytics(self):
        self.cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = self.cursor.fetchall()
        
        if not data:
            messagebox.showinfo("Analytics", "No expenses to show!")
            return
        
        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]
        
        plt.figure(figsize=(6,6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        plt.title("Expense Breakdown")
        plt.show()

    def search_expense(self):
        search_term = self.amount_entry.get()
        search_date = self.date_entry.get()
        search_category = self.category_entry.get()

        self.tree.delete(*self.tree.get_children())

        query = "SELECT * FROM expenses WHERE amount=? OR date=? OR category=?"
        self.cursor.execute(query, (search_term, search_date, search_category))

        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)


    def filter_expense(self):
        category = self.filter_category.get()
        self.tree.delete(*self.tree.get_children())

        if category == "All" or not category:
            self.show_expenses()
        else:
            self.cursor.execute("SELECT * FROM expenses WHERE category=?", (category,))
            for row in self.cursor.fetchall():
                self.tree.insert("", "end", values=row)

    def toggle_expense_list(self):
        if self.expense_visible:
            self.expense_frame.pack_forget()
        else:
            self.expense_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)
        self.expense_visible = not self.expense_visible

    def show_expenses(self):
        self.cursor.execute("SELECT * FROM expenses")
        records = self.cursor.fetchall()
        
        # If no records exist, avoid unnecessary clearing
        if not records:
            return  

        for row in records:
            if not self.tree.exists(row[0]):  # Insert only if it doesn't exist
                self.tree.insert("", "end", values=row)





if __name__ == "__main__":
    root = Tk()
    ExpenseTracker(root)
    root.mainloop()
