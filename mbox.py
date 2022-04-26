import copy
import tkinter.messagebox

import _tkinter
from tkinter import *
from tkinter import ttk


class Mbox(object):
    root = None

    def __init__(self, headings, rows, index=None, edit=False, callback=None):
        print(index)
        print(rows[index])
        self.callback = callback
        self.edit = edit
        self.index = index
        self.headings = headings
        self.entries = []
        self.top = Toplevel(Mbox.root)
        self.top.title("Insert new record" if not edit else "Edit record")
        frame = Frame(self.top, borderwidth=4, relief='ridge')
        frame.grid(column=0, row=0, sticky="NSEW")

        n = len(headings)

        # add grid rows for inputs
        for i in range(n + 1):
            frame.rowconfigure(i, weight=1)
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=7)

        # add inputs
        for i in range(len(headings)):
            if i == 0:  # does not let the user modify the id row
                continue
            label = Label(frame, text=headings[i])
            label.grid(column=0, row=i, padx=4, pady=4)
            entry = Entry(frame)
            if edit:
                entry.insert(END, str(rows[index][i]))

            entry.grid(column=1, row=i)
            self.entries.append(entry)

        # submit button
        b_submit = Button(frame, text='Submit')
        b_submit['command'] = lambda: self.proceed(rows)
        b_submit.grid(column=0, row=n)

        # cancel button
        b_cancel = Button(frame, text='Cancel', command=self.top.destroy)
        b_cancel.grid(column=1, row=n, padx=4, pady=4)

    def proceed(self, rows):
        print('self index: ' + str(self.index))
        data = [str(self.index + 1)]
        for entry in self.entries:
            val = entry.get()
            data.append(val)
        if self.edit:  # if user is modifying a row
            rows[self.index] = data
        else:  # else user is inserting a new row
            rows.insert(self.index, data)
            # update the id of the remaining rows
            for k in range(self.index + 1, len(rows)):
                rows[k][0] = str(int(rows[k][0]) + 1)
        self.callback()
        self.top.destroy()
