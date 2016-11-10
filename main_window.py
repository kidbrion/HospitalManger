import MySQLdb
from Tkinter import *
import tkMessageBox
import ttk
from add_to_db import select_person
from remove_person import RemovePersonGUI
from pass_required import PassAndEdit
from change_doctor_or_nurse import change_doctor_or_nurse
from patient_report import PatientReport
from employee_report import EmployeeReport
class main_window:
    conn = None
    # DB connection parameters
    db_ip = None
    db_user = None
    db_pass = None
    db_name = None
    action_lb = None
    select_window = None
    padx = 50
    pady = 15

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open connection for DB
        self.db_ip = db_ip
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pass, db=db_name)
        cursor = conn.cursor()
        self.select_window = Tk()

        self.select_window.wm_title("Select an action")

        img = PhotoImage(file='hospital-icon-20.gif')
        self.select_window.tk.call('wm', 'iconphoto', self.select_window._w, img)


        # label, entry and button shown
        enter_select_label = Label(self.select_window, text="Select an action:", font=("Helvetica", 16))
        enter_select_label.grid(padx=self.padx, pady=self.pady, row=0, column=0, columnspan=2)

        opt_type_list = ['Add person', 'Remove person', 'Change details', 'Change treating Doctor/Nurse', 'Report for patient', 'Report for nurse/doctor' ]
        self.action_lb = Listbox(self.select_window, width=30)
        j = 0

        for opt in opt_type_list:
            self.action_lb.insert(j, opt)
            j += 1

        self.action_lb.select_set(0)
        self.action_lb.grid(padx=self.padx, pady=self.pady, row=1, column=0, columnspan=2)

        ok_button = Button(self.select_window, text="OK", width=10, command=self.open_selection)
        ok_button.grid(padx=self.padx, pady=self.pady, row=2, column=0, columnspan=2)

        self.select_window.mainloop()


    def open_selection(self):
        action = self.action_lb.get(ACTIVE)
        if action == 'Add person':
            select_person(self.db_ip, self.db_user, self.db_pass, self.db_name)
        elif action == 'Remove person':
            RemovePersonGUI(self.db_ip, self.db_user, self.db_pass, self.db_name)
        elif action == 'Change details':
            PassAndEdit(self.db_ip, self.db_user, self.db_pass, self.db_name)
        elif action == 'Change treating Doctor/Nurse':
            change_doctor_or_nurse(self.db_ip, self.db_user, self.db_pass, self.db_name)
        elif action == 'Report for patient':
            PatientReport(self.db_ip, self.db_user, self.db_pass, self.db_name)
        elif action == 'Report for nurse/doctor':
            EmployeeReport(self.db_ip, self.db_user, self.db_pass, self.db_name)


main_window("localhost", "root", "Polina161", "hospital")