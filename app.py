import copy
import tkinter.messagebox
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from functools import partial
import mbox
import csv
import os

# global variables
filename = ""
clicked_col = -1
clicked_row = -1
headers = []  # column names
rows = []  # rows array that contain the data
rows_display = []  # rows array for display purpose
rv = False  # reverse sort
sorted_col = -1  # column currently being sorted

root = Tk()
root.title('Sales manager')
content = ttk.Frame(root, padding=(3, 3, 12, 12))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=2)
content.rowconfigure(0, weight=1)
content.rowconfigure(1, weight=10)
content.rowconfigure(2, weight=1)

# Navigation bar
navbar = Menu(root)
root.config(menu=navbar)


def select_file():
    global filename
    filename = fd.askopenfilename(
        title='Select a CSV',
        initialdir='/',
        filetypes=(('CSV files', '*.csv'),))
    if filename is None or filename == "":  # if the user cancelled
        return
    read_file()
    sort_data(0)  # initial sort, IMPORTANT!! DO NOT REMOVE OR ELSE A BUG WILL APPEAR AT THE FIRST INSERTION
    display_data()


def read_file():
    global filename, rows, rows_display, headers
    with open(filename, mode="r", encoding="latin1") as f:
        lines = f.readlines()
        rows = []
        # csv reader needed because some product names have commas in them
        for line in csv.reader(lines[1:], quotechar='"', delimiter=',', quoting=csv.QUOTE_MINIMAL):
            rows.append(line)
        headers = lines[0].strip().split(',')
    root.title(filename)
    rows_display = rows


def save_as():
    global filename, rv, sorted_col, rows_display
    fname = fd.asksaveasfilename(defaultextension=".csv", filetypes=(('CSV files', '*.csv'),))
    if fname is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return

    with open(fname, mode="w", newline='', encoding='latin1') as f:
        # Commented out because this method doesn't account for commas in the product name
        # csv_data = ",".join(headers) + "\n"
        # csv_data += "\n".join([','.join(row) for row in rows])
        # f.write(csv_data)

        w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        w.writerows(rows)

    # open the newly saved file
    filename = fname
    read_file()

    # preserve the current search
    if search_entry.get() is not None and search_entry.get() != "":
        rows_display = rows
        search()

    # preserve sorting
    rv = not rv
    sort_data(sorted_col)

    text.configure(text="Saved file")
    return


def save():
    global filename
    with open(filename, mode="w", newline='', encoding='latin1') as f:

        # Commented out because it doesn't account for commas in the product name
        # csv_data = ",".join(headers) + "\n"
        # csv_data += "\n".join([','.join(row) for row in rows])
        # f.write(csv_data)
        # f.close()

        w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(headers)
        w.writerows(rows)
    root.title(filename)
    text.configure(text="Saved file")
    f.close()
    return


file_menu = Menu(navbar, tearoff=False)
navbar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=select_file)
file_menu.add_command(label="Save", command=save)
file_menu.add_command(label="Save As", command=save_as)

# Top toolbar section
toolbar = ttk.Frame(content)
toolbar.columnconfigure(0, weight=1)
toolbar.columnconfigure(1, weight=1)
toolbar.columnconfigure(2, weight=1)
toolbar.columnconfigure(3, weight=1)
toolbar.columnconfigure(4, weight=1)
toolbar.columnconfigure(5, weight=1)
toolbar.columnconfigure(6, weight=1)
toolbar.columnconfigure(7, weight=1)
toolbar.columnconfigure(8, weight=1)
toolbar.columnconfigure(9, weight=1)
toolbar.columnconfigure(10, weight=1)
toolbar.columnconfigure(12, weight=12)
toolbar.rowconfigure(0, weight=1)


def search():
    phrase = search_entry.get()
    global rows_display, rv, rows
    _rows_display = []
    rows_display = rows
    # preserve sorting
    rv = not rv
    sort_data(sorted_col)
    for i in range(len(rows_display)):
        match = False
        for j in range(len(rows_display[i])):
            cell = rows_display[i][j]
            start = cell.lower().find(phrase.lower())
            if start != -1: # if the phrase is found
                match = True
        if match:
            _rows_display.append(rows_display[i])
    rows_display = _rows_display
    display_data()
    text.configure(text=f"Found {len(rows_display)} matching record(s)")


# Toolbar options
search_label = ttk.Label(toolbar, text="Phrase")
search_entry = ttk.Entry(toolbar)
search_btn = ttk.Button(toolbar, text="Search", command=search)

# Align the options
search_label.grid(column=0, row=0, sticky="NEW")
search_entry.grid(column=1, row=0, sticky="NEW")
search_btn.grid(column=3, row=0, sticky="NEW")

# Middle frame
frame = ttk.Frame(content, relief="ridge", width=1200, height=800)
frame.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)

# Treeview to display csv content
databox = ttk.Treeview(frame)

# Bottom area
bottom_area = ttk.Frame(content)
bottom_area.columnconfigure(0, weight=1)
bottom_area.rowconfigure(0, weight=1)

# Bottom area
text = Label(bottom_area, bg="SILVER")

# Align the areas above
content.grid(column=0, row=0, sticky="NSEW")
frame.grid(column=0, row=1, sticky="NSEW")
databox.grid(column=0, row=0, sticky="NSEW")
toolbar.grid(column=0, row=0, sticky="NSEW")
bottom_area.grid(column=0, row=2, sticky="NSEW")
text.grid(column=0, row=0, columnspan=11, sticky="NEWS")


def find_mean():
    s = 0
    for i in range(len(rows)):
        try:
            s += float(rows[i][clicked_col])
        except:
            text.configure(text="Unsupported column")
            return
    avg = s / len(rows)
    text.configure(text=f"Mean of the {headers[clicked_col]} column is: {avg}")


def find_largest():
    lg = -10000000
    for i in range(len(rows)):
        try:
            val = float(rows[i][clicked_col])
        except:
            text.configure(text="Unsupported column")
            return
        if val > lg:
            lg = val
    text.configure(text=f"Largest value of the {headers[clicked_col]} column is: {lg}")


def find_smallest():
    sm = 1000000000
    for i in range(len(rows)):
        try:
            val = float(rows[i][clicked_col])
        except:
            text.configure(text="Unsupported column")
            return
        if val < sm:
            sm = val
    text.configure(text=f"Smallest value of the {headers[clicked_col]} column is: {sm}")


def insert_row():
    global headers, rows, rows_display, rv

    # preserve the current search
    if search_entry.get() is not None and search_entry.get() != "":
        rows_display = rows
        search()

    # preserve the current sorting
    rv = not rv
    sort_data(sorted_col)

    display_data()
    text.configure(text="Inserted new row")

    # add a star indicating that there are unsaved changes
    root.title(filename + "*")


def edit_row():
    global headers, rows, rows_display, rv

    # preserve the current search
    if search_entry.get() is not None and search_entry.get() != "":
        rows_display = rows
        search()

    # preserve the current sorting
    rv = not rv
    sort_data(sorted_col)

    display_data()
    text.configure(text="Updated row")

    # add a star indicating that there are unsaved changes
    root.title(filename + "*")


def delete_row():
    global rows, rows_display, rv
    answer = tkinter.messagebox.askyesno(title="Delete row", message="Proceed to delete row?")
    if answer:
        rows.pop(clicked_row)
        # shift the row id of the remaining rows
        for k in range(clicked_row, len(rows)):
            rows[k][0] = str(int(rows[k][0]) - 1)

        # preserve the current search
        if search_entry.get() is not None and search_entry.get() != "":
            rows_display = rows
            search()

        # preserve the current sorting
        rv = not rv
        sort_data(sorted_col)

        # add a star indicating that there are unsaved changes
        root.title(filename + "*")
        text.configure(text="Deleted row")


# Popups
popup_col = Menu(root, tearoff=False)  # menu popup when clicking on the column header
popup_row = Menu(root, tearoff=False)  # menu popup when clicking on the row
# Pop up window
mb = mbox.Mbox
mb.root = root

# Adding Menu Items
popup_col.add_command(label="Find column's mean", command=find_mean)
popup_col.add_command(label="Find column's largest", command=find_largest)
popup_col.add_command(label="Find column's smallest", command=find_smallest)

popup_row.add_command(label="Insert before",
                      command=lambda: mb(headers, rows, index=clicked_row, callback=insert_row))
popup_row.add_command(label="Edit row",
                      command=lambda: mb(headers, rows, index=clicked_row, edit=True, callback=edit_row))
popup_row.add_command(label="Delete row",
                      command=delete_row)


def menu_popup(event):
    global clicked_col, clicked_row

    # display the popup menu
    try:
        clicked_col = int(databox.identify_column(event.x).replace("#", "")) - 1
        if databox.identify_row(event.y) != "":  # if the user click on somewhere else instead of the header
            # display the menu for rows
            popup_row.tk_popup(event.x_root, event.y_root, 0)
            clicked_row = int(databox.identify_row(event.y)) - 1
        else:
            # display the menu for columns
            popup_col.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # Release the grab
        popup_col.grab_release()
        popup_row.grab_release()


# Bind so that right-clicking now pops up the menu
if os.name == 'posix':
    databox.bind("<Button-2>", menu_popup)
else:
    databox.bind("<Button-3>", menu_popup)


def sort_data(col):
    global rows, rows_display, rv, sorted_col

    if sorted_col == col:
        rv = not rv
    else:
        rv = False
    sorted_col = col

    # if there's a search going on, sort based on the current search result
    sort_target = rows if search_entry.get() is None or search_entry.get() == "" else rows_display
    try:
        # try sorting by integer value
        rows_display = sorted(sort_target, key=lambda x: int(x[col]), reverse=rv)
    except:
        # else try sorting by date value
        try:
            rows_display = sorted(sort_target, key=lambda x: (
                int(x[col].split('/')[2]), int(x[col].split('/')[0]), int(x[col].split('/')[1])),
                                  reverse=rv)
        # else sort by string value
        except:
            rows_display = sorted(sort_target, key=lambda x: x[col], reverse=rv)
    display_data()


def display_data():
    global rows, rows_display, rv
    # clear the tree view
    for item in databox.get_children():
        databox.delete(item)

    # declare column names
    databox['columns'] = headers
    databox.column('#0', width=0)  # default #0 column
    i = 0

    # add column names to the treeview
    for header in headers:
        if header == "Product Name":
            databox.column(header, anchor="center", width=550)
        else:
            databox.column(header, anchor="center", width=105)
        # add a symbol next to the sorted column if a column is being sorted
        if sorted_col == i:
            # add up/down arrow
            symbol = "  " + u"\u25B2" if rv else "  " + u"\u25BC"
            databox.heading(header, text=header + symbol, anchor="center",
                            command=partial(sort_data, i))  # preserve i in function call
        else:
            databox.heading(header, text=header, anchor="center",
                            command=partial(sort_data, i))  # preserve i in function call
        i += 1

    # add data rows
    for row in rows_display:
        databox.insert(parent="", index="end", iid=row[0], text='', values=row)


root.mainloop()
