import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox # themed libraries for 

class DatabaseManagerApp:
    def __init__(self, root):
        # create main application window
        self.root = root
        self.root.title("Database Manager")
        # maximize window
        try:
            self.root.state('zoomed')
        # in case zoomed doesn't work (mac and linux typically ignore this)
        except:
            # Get screen width and height
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            # Manually set window geometry to screen size
            root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Connect to SQLite database
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

        # UI Variables
        self.table_names = ["Authors", "Books", "Customers", "Orders", "Order Items"]
        self.selected_table = tk.StringVar(value="Select a Table")
        self.remove_row = tk.StringVar(value="Remove Row")
        self.save_db = tk.StringVar(value="Save Changes")

        #columns for the tables to fill under
        self.schemas = {
            "Authors": ["AuthorID", "Name", "Bio"],
            "Books": ["BookID", "Title", "AuthorID", "Price", "PublishedDate"],
            "Customers": ["CustomerID", "FirstName", "LastName", "Email"],
            "Orders": ["OrderID", "CustomerID", "OrderDate", "Status"],
            "OrderItems": ["OrderItemID", "OrderID", "BookID", "Quantity", "Price"]
        }
        # gets the id (primary key) of a row for changing it or removing it
        self.primary_keys = {
            "Authors": "AUTHORID",
            "Books": "BOOKID",
            "Customers": "CUSTOMERID",
            "Orders": "ORDERID",
            "OrderItems": "ORDERITEMID"
        }

        # UI Setup
        self.create_widgets()
        self.create_button_frame() # button frame for inserting/editing of table rows

    def build_entry_form(self, table, submit_callback, default_values=None): # helper function for insertRow and editRow
        def create_field(label_text, var_type=tk.StringVar, default_value=""): # create a single user prompt and entry for row insertion
            var = var_type()
            var.set(default_value)
            label = ttk.Label(self.button_frame, text=label_text) 
            label.pack(pady=10)
            entry = ttk.Entry(self.button_frame, textvariable=var, width=10)
            entry.pack(pady=10)
            return var

        for widget in self.button_frame.winfo_children(): # reset the button frame upon new operation
            widget.destroy()
        table = table.replace(" ", "") # table entries have spaces, internal database does not.
        entry_list = [] 

        match table: # create the user prompts based on table selected
            case "Authors":
                fields = [
                    ("enter value for AuthorID(int)", tk.StringVar),
                    ("enter value for author's name (String)", tk.StringVar),
                    ("enter author's biography (string)", tk.StringVar)
                ]
            case "Books":
                fields = [
                    ("enter value for book id (integer)", tk.StringVar),
                    ("enter the title of the book (string)", tk.StringVar),
                    ("enter the id of the Author (integer)", tk.StringVar),
                    ("enter Price (double)", tk.StringVar),
                    ("enter date of publication", tk.StringVar)
                ]
            case "Customers":
                fields = [
                    ("enter the value for Customer id (Integer)", tk.StringVar),
                    ("enter the first name of customer (string)", tk.StringVar),
                    ("enter the last name of customer (string)", tk.StringVar),
                    ("enter the email address (string)", tk.StringVar)
                ]
            case "Orders":
                fields = [
                    ("enter order id (integer)", tk.StringVar),
                    ("enter customer id (integer)", tk.StringVar),
                    ("enter date of order placed (01/05/2005)", tk.StringVar),
                    ("enter the status (string)", tk.StringVar)
                ]
            case "OrderItems":
                fields = [
                    ("enter value of the OrderItemID (integer)", tk.StringVar),
                    ("enter the number of OrderID(integer)", tk.StringVar), 
                    ("enter the number of the BookID(integer)", tk.StringVar), 
                    ("enter the number of Quantity (integer)", tk.StringVar), 
                    ("enter the value for the Price (double)", tk.StringVar)
                ]

        for i, (label_text, var_type) in enumerate(fields):
            # refill the text boxes with entries already existing if 
            # editing a preexisting row.
            default_value = default_values[i] if default_values else ""
            # create a single user prompt and entry for row insertion. 
            var = create_field(label_text, var_type, default_value) 
            entry_list.append(var) # add user entry to the list

        button = tk.Button(self.button_frame, text="Submit all entries", 
                            command=lambda: submit_callback(table, entry_list))
        button.pack(pady=5)
        self.root.bind('<Return>', lambda event: button.invoke())

    def create_widgets(self): # the main menu
        # Dropdown Menu
        dropdown = tk.OptionMenu(self.root, self.selected_table, *self.table_names)
        dropdown.pack(pady=5)

        # Buttons
        btn_get = tk.Button(self.root, text="Get Table", command=self.get_table)
        btn_get.pack(pady=2)

        btn_insert = tk.Button(self.root, text="Insert Row into Table", command=self.insertRow)
        btn_insert.pack(pady=2)

        btn_del = tk.Button(self.root, text="Delete Row", command=self.deleteRow)
        btn_del.pack(pady=2)

        btn_save = tk.Button(self.root, text="Save Changes", command=self.save_changes)
        btn_save.pack(pady=2)

        # Treeview (Table Output)
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.updateTreeView) # debug code

        self.tree.bind("<Double-1>", lambda event: self.editRow(event)) # edit row in tree view on double click

        # Scrollbars
        scroll_x = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        scroll_y = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

    def create_button_frame(self): # the interface for user input (used for editing/inserting rows)
        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, height=300)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.button_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")

    def deleteRow(self):
        row_id = self.tree.focus() # get the row that is highlighted by mouse click
        if not row_id:
            messagebox.showwarning("User Error", "No selection,\nPlease select a row to delete.")
            return

        # get the id of the row (first column)
        values = self.tree.item(row_id, "values") 
        pk_value = values[0] 

        table = self.selected_table.get().replace(" ", "")

        # Confirm before deleting
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this row?")
        if not confirm:
            return

        self.execute_db_action(table, entry_list=[], action="delete", row_id=pk_value) 

    def editRow(self, event):
        table = self.selected_table.get()
        row_id = self.tree.identify_row(event.y) # see where the mouse was on double click
        if not row_id:
            messagebox.showwarning("User error", "cannot change blank row")
            return 0 # cancel edit operation
        values = self.tree.item(row_id, "values") # see what row was highlighted, not looking at the mouse location
        id = values[0] # first index of values is where the row id is
        # call the helper function
        self.build_entry_form(table, lambda t, entries: self.execute_db_action(t, 
                                                                               entries, 
                                                                               action="update", 
                                                                               row_id=id), 
                                                                               default_values=values)
    # lambda t, self.execute_db_action is a custom callback, to call 
    # execute_db_entry function with the same parameters when code 
    # gets to "submit callback"

    def execute_db_action(self, table, entry_list, action, row_id=None): # a helper function for manipulating the database for insert, edit and deleteRow
        # get columns from selected table for dynamic sql query construction
        fields = self.schemas.get(table) 
        # get every user entry without trailing whitespace
        values = [entry.get().strip() for entry in entry_list]

        # create an sql query based on the required operation
        if action == "insert":
            # get new entries from the user input
            new_entries = ", ".join(["?"] * len(fields))
            field_str = ", ".join(fields) 
            query = f"INSERT INTO {table} ({field_str}) VALUES ({new_entries})"

        elif action == "update":
            # get columns where user will set edited entries
            set_clause = ", ".join([f"{field} = ?" for field in fields]) 
            print(set_clause) # debug code
            # get primary keys from dictionary based on table selected
            pk_column = self.primary_keys.get(table) 
            query = f"UPDATE {table} SET {set_clause} WHERE {pk_column} = ?"
            values.append(row_id)

        elif action == "delete":
            pk_column = self.primary_keys.get(table)
            if not pk_column:
                messagebox.showerror("Error", f"No primary key for table '{table}'")
                return
            query = f"DELETE FROM {table} WHERE {pk_column} = ?"
            values = [row_id]

        else:
            messagebox.showerror("Error", f"Unknown action: {action}")
            return

        print(query, values) #debug
        
        pk_field = self.schemas[table][0] # get the row id for warning message box
        # Validate ID 
        if not values[0]:
            messagebox.showwarning("Missing Field", f"{pk_field} cannot be empty.")
            return
        try:
            int(values[0])
        # check that id is a number
        except ValueError:
            messagebox.showwarning("Invalid Field", "ID must be a number.")
            return
        
        # execute the database operation
        try:
            self.cursor.execute(query, values)
            self.get_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_table(self):
        table = self.selected_table.get()
        # delete button frame from any potential insert/edit operation
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        if table == "Select a Table": # prompt user to make a selection if not
            messagebox.showwarning("User Error", "No Selection\nPlease select a table.")
            return
        table = table.replace(" ", "") # again, internally the values have no spaces
        try:
            df = pd.read_sql_query(f"SELECT * FROM '{table}'", self.connection)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear previous data
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        for row in df.itertuples(index=False):
            self.tree.insert("", "end", values=row)

    def insertRow(self):
        table = self.selected_table.get()
        if table == "Select a Table":
            messagebox.showwarning("User Error", "No Selection\nPlease select a table.")
            return
        table = table.replace(" ", "")
        self.build_entry_form(table, lambda t, entries: self.execute_db_action(t, 
                                                                                entries, 
                                                                                action="insert", 
                                                                                row_id=None), 
                                                                                default_values=None)
        
    def save_changes(self):
        try:
            self.connection.commit()
            messagebox.showinfo("Success", "Changes saved to the database.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def updateTreeView(self, event=None): # debugging function
        selected_nodes = self.tree.selection()
        for node in selected_nodes:
            values = self.tree.item(node, "values")
            print(f"Selected row {node} with values: {values}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseManagerApp(root)
    root.mainloop()
