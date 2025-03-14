import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
from datetime import datetime, timedelta

# Connecting to Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
    '''CREATE TABLE IF NOT EXISTS Library (
        BK_NAME TEXT, 
        BK_ID TEXT PRIMARY KEY NOT NULL, 
        AUTHOR_NAME TEXT, 
        BK_STATUS TEXT, 
        CARD_ID TEXT,
        BOOK_TAKEN_DATE TEXT,
        EXPECTED_RETURN_DATE TEXT
    )'''
)

# Tkinter Root Window
root = Tk()
root.title('Library Management System')
root.geometry('1050x550')
root.configure(bg='#f0f0f0')
root.resizable(0, 0)

# Tkinter Variables
bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()
book_taken_date = StringVar()
expected_return_date = StringVar()

def issuer_card():
    Cid = sd.askstring('Issuer Card ID', "Enter Issuer's Card ID:")
    if not Cid:
        mb.showerror('Issuer ID cannot be empty!', 'Please provide an Issuer ID.')
    return Cid

def display_records():
    tree.delete(*tree.get_children())
    curr = connector.execute('SELECT * FROM Library')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)

def clear_fields():
    bk_status.set('Available')
    bk_id.set('')
    bk_name.set('')
    author_name.set('')
    card_id.set('')
    book_taken_date.set('')
    expected_return_date.set('')
    bk_id_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
        book_taken_date.set(datetime.today().strftime('%Y-%m-%d'))
        expected_return_date.set((datetime.today() + timedelta(days=14)).strftime('%Y-%m-%d'))
    else:
        card_id.set('N/A')
        book_taken_date.set('N/A')
        expected_return_date.set('N/A')
    surety = mb.askyesno('Confirm?', 'Are you sure you want to add this record?')
    if surety:
        try:
            connector.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID, BOOK_TAKEN_DATE, EXPECTED_RETURN_DATE) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get(), book_taken_date.get(), expected_return_date.get()))
            connector.commit()
            clear_and_display()
            mb.showinfo('Success', 'Record added successfully!')
        except sqlite3.IntegrityError:
            mb.showerror('Error', 'Book ID already exists!')

def delete_record():
    selected_item = tree.selection()
    if not selected_item:
        mb.showerror('Error', 'Please select a record to delete!')
        return
    book_id = tree.item(selected_item)['values'][1]
    surety = mb.askyesno('Confirm?', 'Are you sure you want to delete this record?')
    if surety:
        connector.execute('DELETE FROM Library WHERE BK_ID=?', (book_id,))
        connector.commit()
        clear_and_display()

def update_record():
    selected_item = tree.selection()
    if not selected_item:
        mb.showerror('Error', 'Please select a record to update!')
        return
    book_id = tree.item(selected_item)['values'][1]
    surety = mb.askyesno('Confirm?', 'Are you sure you want to update this record?')
    if surety:
        connector.execute(
            'UPDATE Library SET BK_NAME=?, AUTHOR_NAME=?, BK_STATUS=?, CARD_ID=?, BOOK_TAKEN_DATE=?, EXPECTED_RETURN_DATE=? WHERE BK_ID=?',
            (bk_name.get(), author_name.get(), bk_status.get(), card_id.get(), book_taken_date.get(), expected_return_date.get(), book_id))
        connector.commit()
        clear_and_display()

# UI Setup
Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Arial", 18, 'bold'), bg='#004080', fg='white', pady=10).pack(side=TOP, fill=X)

left_frame = Frame(root, bg='white', padx=20, pady=20)
left_frame.place(x=10, y=50, width=300, height=480)

Label(left_frame, text='Book Name:', font=('Arial', 12)).pack(anchor=W)
bk_name_entry = Entry(left_frame, textvariable=bk_name, font=('Arial', 12), width=30)
bk_name_entry.pack(pady=5)

Label(left_frame, text='Book ID:', font=('Arial', 12)).pack(anchor=W)
bk_id_entry = Entry(left_frame, textvariable=bk_id, font=('Arial', 12), width=30)
bk_id_entry.pack(pady=5)

Label(left_frame, text='Author Name:', font=('Arial', 12)).pack(anchor=W)
author_name_entry = Entry(left_frame, textvariable=author_name, font=('Arial', 12), width=30)
author_name_entry.pack(pady=5)

Label(left_frame, text='Status:', font=('Arial', 12)).pack(anchor=W)
status_dropdown = ttk.Combobox(left_frame, textvariable=bk_status, values=('Available', 'Issued'), font=('Arial', 12), width=28)
status_dropdown.pack(pady=5)

Button(left_frame, text='Add Record', command=add_record, font=('Arial', 12, 'bold'), bg='#28a745', fg='white', padx=10, pady=5).pack(pady=5)
Button(left_frame, text='Update Record', command=update_record, font=('Arial', 12, 'bold'), bg='#007bff', fg='white', padx=10, pady=5).pack(pady=5)
Button(left_frame, text='Delete Record', command=delete_record, font=('Arial', 12, 'bold'), bg='#dc3545', fg='white', padx=10, pady=5).pack(pady=5)

# Treeview Widget
tree_frame = Frame(root)
tree_frame.place(x=320, y=50, width=710, height=480)

tree = ttk.Treeview(tree_frame, columns=('BK_NAME', 'BK_ID', 'AUTHOR_NAME', 'BK_STATUS', 'CARD_ID', 'BOOK_TAKEN_DATE', 'EXPECTED_RETURN_DATE'), show='headings')
for col in ('BK_NAME', 'BK_ID', 'AUTHOR_NAME', 'BK_STATUS', 'CARD_ID', 'BOOK_TAKEN_DATE', 'EXPECTED_RETURN_DATE'):
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill=BOTH, expand=True)

clear_and_display()
root.mainloop()