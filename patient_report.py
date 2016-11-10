#!/usr/bin/python
import MySQLdb
from Tkinter import *
import ttk
import tkMessageBox


class PatientReport:
    # choose doctor / nurse
    opt_type_cb = None
    # the first time opt_person_cb is shown
    opt_person_cb = False
    # design parameters
    padx = 50
    pady = 10
    # the main window
    patient_window = None
    # connection to the DB
    conn = None
    # the chosen option from opt_type_list which contains doctor / nurse
    person_type = None
    # the table to select from in queries
    table_name = None
    # Buttons in use:
    get_persons_button = None
    get_person_details_button = None
    # opened_details is a boolean to know if there are any input entries shown right now
    opened_details = False
    # last chosen patient's ID
    curr_patient_id = None
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
        self.patient_window = Toplevel()
        # set window icon
        img = PhotoImage(file='hospital-icon-20.gif')
        self.patient_window.tk.call('wm', 'iconphoto', self.patient_window._w, img)
        self.patient_window.wm_title("Patient Report:")
        self.patient_window.minsize(300, 550)
        # self.employee_window.maxsize(300, 550)

        self.choose_type_label = Label(self.patient_window, text='Show report for a patient:')
        self.choose_type_label.grid(padx=self.padx, pady=self.pady, row=0, column=0, columnspan=2)

        self.get_person_opt()
        self.patient_window.mainloop()

    def get_person_opt(self):
        cursor = self.conn.cursor()
        self.table_name = "patients"
        # reset a list for all the people from this person type on the DB
        person_opt_names = []
        # get name & id of each person matching the chosen type, which is still relevant (the end date is NULL).
        # each field in the tables nurses, doctors and patients is in this format:
        # *person type*_*field info* (e.g. patient_id and doctor_id)
        sql_query = "select patient_id, patient_name " \
                    "from patients" \
                    " where end_of_treat_date is NULL or end_of_treat_date > now() " \
                    " order by patient_name;"
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
            self.opt_person_cb = ttk.Combobox(self.patient_window, state='readonly', values=person_opt_names)
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
        self.get_person_details_button = Button(self.patient_window, text="Open Patient Report", width=20,
                                                command=self.get_report)
        self.get_person_details_button.grid(padx=self.padx, pady=self.pady, row=4, column=0, columnspan=2)

    def destroy_report_gui(self):
        if self.opened_details:
            # hide every old detail input field (in case that we change the chosen person / person_type)
            self.id_label.grid_forget()
            self.get_person_details_button.grid_forget()
            # self.scrollbar.grid_forget()

    def get_report(self):
        # the information we get from the query
        results = []
        # mark that there are fields for editing details
        self.opened_details = True
        # design parameter
        padx_details = 10
        patient_id_name = self.opt_person_cb.get()
        patient_id = patient_id_name.split(", ")[0]
        # save this person_id, in case that it will be changed by the user
        self.curr_patient_id = patient_id
        cursor = self.conn.cursor()
        sql_query_nurse = "select n.nurse_id, n.nurse_name " \
                          "from patients as p, nurses as n " \
                          "where p.treating_nurse_id = n.nurse_id AND p.patient_id = " + self.curr_patient_id
        cursor.execute(sql_query_nurse)
        result_set_nurse = cursor.fetchall()
        sql_query_doctor = "select distinct d.doctor_id, d.doctor_name " \
                           "from patients as p, doctors as d, doctors_patients as dp " \
                           "where dp.pat_id = " + self.curr_patient_id + " AND dp.doctor_id = d.doctor_id "
        cursor.execute(sql_query_doctor)
        result_set_doctor = cursor.fetchall()
        # define GUI elements
        self.id_label = Label(self.patient_window, text="Employees' ID & Name: ")
        self.id_label.grid(padx=padx_details, pady=self.pady, row=5, column=0)
        # self.report_box = Listbox(self.patient_window, yscrollcommand=self.scrollbar.set)
        # self.scrollbar = Scrollbar(self.report_box)

        self.report_box = Listbox(self.patient_window)
        self.scrollbar = Scrollbar(self.report_box, orient=VERTICAL)
        self.report_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.report_box.yview)

        for row in result_set_nurse:
            results.append(row[0] + ", " + row[1])
        for row in result_set_doctor:
            results.append(row[0] + ", " + row[1])
        j = 0
        for row in results:
            self.report_box.insert(j, row)
            j += 1

        self.scrollbar.config(command=self.report_box.yview)

        self.report_box.grid(row=6, column=0, rowspan=4, columnspan=2, sticky=N + E + S + W)

        self.report_box.columnconfigure(0, weight=1)
        self.scrollbar.grid(column=1, sticky=N + E + S + W)


#PatientReport("hospital", "guess45does", "root", "localhost")
