#!/usr/bin/python
import MySQLdb
from Tkinter import *
import ttk
import tkMessageBox


class EmployeeReport:
    # choose doctor / nurse
    opt_type_cb = None
    # the first time opt_person_cb is shown
    opt_person_cb = False
    # design parameters
    padx = 50
    pady = 10
    # the main window
    employee_window = None
    # connection to the DB
    conn = None
    # the chosen option from opt_type_list which contains doctor / nurse
    person_type = None
    # the table to select from in queries
    table_name = None
    # Buttons in use:
    get_persons_button = None
    get_person_details_button = False
    # opened_details is a boolean to know if there are any input entries shown right now
    opened_details = False
    # last chosen employee's ID
    curr_employee_id = None
    # Labels in use:
    choose_type_label = None
    id_label = None
    name_label = None
    depart_label = None
    license_label = None
    # Entries in use:
    id_entry = None
    name_entry = None
    license_entry = None
    # Report listbox
    report_box = None
    # Report scrollbar
    scrollbar = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open a connection
        self.conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pass, db=db_name)
        self.employee_window = Toplevel()
        # set window icon
        img = PhotoImage(file='hospital-icon-20.gif')
        self.employee_window.tk.call('wm', 'iconphoto', self.employee_window._w, img)
        self.employee_window.wm_title("Employee Report:")
        self.employee_window.minsize(300, 550)
        # self.employee_window.maxsize(300, 550)

        cursor = self.conn.cursor()

        self.choose_type_label = Label(self.employee_window, text='Show report for a:')
        self.choose_type_label.grid(padx=self.padx, pady=self.pady, row=0, column=0, columnspan=2)

        opt_type_list = ['Doctor', 'Nurse']
        self.opt_type_cb = ttk.Combobox(self.employee_window, state='readonly', values=opt_type_list)
        self.opt_type_cb.current(0)
        self.opt_type_cb.grid(padx=self.padx, pady=self.pady, row=1, column=0, columnspan=2)

        get_persons_button = Button(self.employee_window, text="Open Selection", width=20, command=self.get_person_opt)
        get_persons_button.grid(padx=self.padx, pady=self.pady, row=2, column=0, columnspan=2)
        self.employee_window.mainloop()

    def get_person_opt(self):
        cursor = self.conn.cursor()
        self.person_type = self.opt_type_cb.get()
        # all the person types match the DB's table names, with an 'S' in the end
        self.table_name = self.person_type + "s"
        # reset a list for all the people from this person type on the DB
        person_opt_names = []
        end_date_col = self.person_type + "_end_of_employ_date"
        # get name & id of each person matching the chosen type, which is still relevant (the end date is NULL).
        # each field in the tables nurses, doctors and patients is in this format:
        # *person type*_*field info* (e.g. patient_id and doctor_id)
        sql_query = "select " + self.person_type + "_id,  " + self.person_type + "_name " \
                                                                                 "from " + self.table_name + \
                    " where " + end_date_col + " is NULL or " + end_date_col + " > now() " \
                                                                               " order by " + self.person_type + "_name;"
        # to check if a fired person should have a report?!
        cursor.execute(sql_query)
        result_set = cursor.fetchall()

        if cursor.rowcount == 0:
            self.destroy_report_gui()
            tkMessageBox.showinfo("Something Went Wrong...", "Not available " + self.table_name.lower())
            return

        # put all the id and names in a list, separated by ", "
        for row in result_set:
            person_opt_names.append(row[0] + ", " + row[1])
        # opt_person_cb = False means it is the first time this combobox is shown, therefore there is no need to update
        # it, in case that the user has chosen another option from opt_type_cb
        if not self.opt_person_cb:
            self.opt_person_cb = ttk.Combobox(self.employee_window, state='readonly', values=person_opt_names)
            self.opt_person_cb.current(0)
            self.opt_person_cb.grid(padx=self.padx, pady=self.pady, row=3, column=0, columnspan=2)
        else:
            # update the opt_person_cb to its new content and update the GUI a step back (without editing fields)
            self.destroy_report_gui()
            # update the person_opt_names to select from
            self.opt_person_cb['values'] = person_opt_names
            self.opt_person_cb['state'] = 'readonly'
            self.opt_person_cb.current(0)
            self.get_person_details_button.grid(padx=self.padx, pady=self.pady, row=4, column=0, columnspan=2)
            self.opt_person_cb.update()
        self.get_person_details_button = Button(self.employee_window, text="Open Employee Report", width=20,
                                                command=self.get_report)
        self.get_person_details_button.grid(padx=self.padx, pady=self.pady, row=4, column=0, columnspan=2)

    def destroy_report_gui(self):
        if self.opened_details:
            # hide every old detail shown field (in case that we change the chosen person / person_type)
            self.id_label.grid_forget()
            self.report_box.grid_forget()
            self.scrollbar.grid_forget()

    def get_report(self):
        # the information we get from the query
        results = []
        # mark that there are fields for editing details
        self.opened_details = True
        # design parameter
        padx_details = 10
        employee_id_name = self.opt_person_cb.get()
        employee_id = employee_id_name.split(", ")[0]
        # save this person_id, in case that it will be changed by the user
        self.curr_employee_id = employee_id
        cursor = self.conn.cursor()
        if self.opt_type_cb.get() == "Nurse":
            sql_query = "select patient_id, patient_name " \
                        "from patients " \
                        "where treating_nurse_id = '" + self.curr_employee_id + "';"
        else:
            sql_query = "select dp.pat_id, p.patient_name " \
                        "from doctors_patients as dp, patients as p " \
                        "where dp.doctor_id = '" + self.curr_employee_id + "' AND p.patient_id = dp.pat_id "
        cursor.execute(sql_query)
        result_set = cursor.fetchall()
        # define GUI elements
        self.id_label = Label(self.employee_window, text="Patients' ID & Name: ")
        self.id_label.grid(padx=padx_details, pady=self.pady, row=5, column=0)

        self.report_box = Listbox(self.employee_window)
        self.scrollbar = Scrollbar(self.report_box, orient=VERTICAL)
        self.report_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.report_box.yview)
        self.scrollbar.config(command=self.report_box.yview)

        for row in result_set:
            results.append(row[0] + ", " + row[1])
        j = 0
        for row in results:
            self.report_box.insert(j, row)
            j += 1
        self.scrollbar.config(command=self.report_box.yview)

        self.report_box.grid(row=6, column=0, rowspan=4, columnspan=2, sticky=N + E + S + W)

        self.report_box.columnconfigure(0, weight=1)
        self.scrollbar.grid(column=1, sticky=N + E + S + W)

#EmployeeReport("hospital", "guess45does", "root", "localhost")
