#!/usr/bin/python
import MySQLdb
from Tkinter import *
import tkMessageBox
from change_details import ChangeDetailsGui


class PassAndEdit:
    # how many times the user tried to enter the correct password
    attempts = 0
    # the entry in which the user enters his password
    entry_pass = None
    # the window that contains all the widgets
    pass_window = None
    # the right password
    edit_pass = None
    # DB connection parameters
    db_ip = None
    db_user = None
    db_pass = None
    db_name = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open connection for DB
        self.db_ip = db_ip
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pass, db=db_name)
        cursor = conn.cursor()
        # get the password
        cursor.execute("select param_value from sys_param where param_name='edit_pass'")
        row = cursor.fetchone()

        self.edit_pass = row[0]
        cursor.close()
        conn.close()

        # design parameters
        padx = 50
        pady = 10
        self.pass_window = Toplevel()

        self.pass_window.wm_title("Login")

        img = PhotoImage(file='hospital-icon-20.gif')
        self.pass_window.tk.call('wm', 'iconphoto', self.pass_window._w, img)
        # label, entry and button shown
        enter_pass_label = Label(self.pass_window, text="Enter Password:")
        enter_pass_label.pack(padx=padx, pady=pady)

        self.entry_pass = Entry(self.pass_window, show="*")
        self.entry_pass.pack(padx=padx, pady=pady)
        self.entry_pass.focus_set()

        ok_button = Button(self.pass_window, text="OK", width=10, command=self.confirm_pass)
        ok_button.pack(padx=padx, pady=pady)

        self.pass_window.mainloop()

    def confirm_pass(self):
        if self.entry_pass.get() == self.edit_pass:
            # password is correct, open the change details GUI
            self.pass_window.destroy()
            ChangeDetailsGui(self.db_name, self.db_pass, self.db_user, self.db_ip)
        else:
            # password is incorrect, increase bad attempts. if it is more than 3 - exit.
            self.attempts += 1
            if self.attempts < 3:
                tkMessageBox.showinfo("Something is not right...", "Wrong Password!")
            else:
                tkMessageBox.showinfo("Something is not right...", "Wrong Password! Too many attempts - exits...")
                self.pass_window.destroy()

#PassAndEdit('hospital', '1056', 'root', 'localhost')
