#!/usr/bin/python
import MySQLdb
from Tkinter import *
import ttk
import tkMessageBox


class ChangeDetailsGui:
    # This GUI allows the user to change doctor / patient / nurse details (id, name, department and license number
    # (for doctors only)).

    # connection to the DB
    conn = None
    # the chosen option from opt_type_list which contains doctor / patient / nurse
    person_type = None
    # the table to select from in queries
    table_name = None
    # opened_details is a boolean to know if there are any input entries shown right now
    opened_details = False
    # translates department_name to department_id
    departments_dict = None
    # a list of all the departments
    departments_names = None
    # last chosen person's ID (in case that the user updates the ID of a person)
    curr_person_id = None
    # GUI Parameters:
    # the main editing window
    edit_window = None
    # design parameters
    padx = 50
    pady = 10
    # ComboBoxes in use:
    # choose doctor / patient / nurse
    opt_type_cb = None
    # choose the person to edit, from the existing ones in the DB. The false value is in order to mark that this is
    # the first time opt_person_cb is shown
    opt_person_cb = False
    # choose a departure, from the existing ones in the DB
    depart_cb = None
    # Labels in use:
    choose_type_label = None
    id_label = None
    name_label = None
    depart_label = None
    license_label = None
    # Buttons in use:
    get_persons_button = None
    update_details_button = None
    get_person_details_button = False
    # Entries in use:
    id_entry = None
    name_entry = None
    license_entry = None

    def __init__(self, db_name, db_pass, db_user, db_ip):
        # open a connection
        self.conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pass, db=db_name)
        self.edit_window = Toplevel()
        # set window icon
        img = PhotoImage(file='hospital-icon-20.gif')
        self.edit_window.tk.call('wm', 'iconphoto', self.edit_window._w, img)
        self.edit_window.wm_title("Edit Details")

        # get all the departments from the DB
        cursor = self.conn.cursor()
        sql_query = "select * " \
                    "from departments;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()
        # reset a list and a dictionary to map the departments from the DB
        self.departments_names = []
        self.departments_dict = {}

        for row in result_set:
            # row[0] - dep_id, row[1] - dep_name
            self.departments_names.append(row[1])
            self.departments_dict[row[1]] = row[0]

        self.choose_type_label = Label(self.edit_window, text='Edit a:')
        self.choose_type_label.grid(padx=self.padx, pady=self.pady, row=0, column=0, columnspan=2)

        opt_type_list = ['Doctor', 'Nurse', 'Patient']
        self.opt_type_cb = ttk.Combobox(self.edit_window, state='readonly', values=opt_type_list)
        self.opt_type_cb.current(0)
        self.opt_type_cb.grid(padx=self.padx, pady=self.pady, row=1, column=0, columnspan=2)

        get_persons_button = Button(self.edit_window, text="Open Selection", width=20, command=self.get_person_opt)
        get_persons_button.grid(padx=self.padx, pady=self.pady, row=2, column=0, columnspan=2)

        self.edit_window.mainloop()

    def get_person_opt(self):
        cursor = self.conn.cursor()
        self.person_type = self.opt_type_cb.get()
        # all the person types match the DB's table names, with an 'S' in the end
        self.table_name = self.person_type + "s"
        # reset a list for all the people from this person type on the DB
        person_opt_names = []
        if self.person_type == 'Patient':
            end_date_col = "end_of_treat_date"
        else:
            end_date_col = self.person_type + "_end_of_employ_date"
        # get name & id of each person matching the chosen type, which is still relevant (the end date is NULL).
        # each field in the tables nurses, doctors and patients is in this format:
        # *person type*_*field info* (e.g. patient_id and doctor_id)
        sql_query = "select " + self.person_type + "_id,  " + self.person_type + "_name " \
                    "from " + self.table_name + \
                    " where " + end_date_col + " is NULL or " + end_date_col + " > now() "\
                    " order by " + self.person_type + "_name;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()

        if cursor.rowcount == 0:
            self.destroy_opt_person_gui()
            self.destroy_details_gui()
            tkMessageBox.showinfo("Something Went Wrong...", "No available " + self.table_name.lower())
            return

        # put all the id and names in a list, separated by ", "
        for row in result_set:
            person_opt_names.append(row[0] + ", " + row[1])
        # opt_person_cb = False means it is the first time this combobox is shown, therefore there is no need to update
        # it, in case that the user has chosen another option from opt_type_cb
        if not self.opt_person_cb:
            self.opt_person_cb = ttk.Combobox(self.edit_window, state='readonly', values=person_opt_names)
            self.opt_person_cb.current(0)
            self.opt_person_cb.grid(padx=self.padx, pady=self.pady, row=3, column=0, columnspan=2)
        else:
            # update the opt_person_cb to its new content and update the GUI a step back (without editing fields)
            self.destroy_details_gui()
            # update the person_opt_names to select from
            self.opt_person_cb['values'] = person_opt_names
            self.opt_person_cb['state'] = 'readonly'
            self.opt_person_cb.current(0)
            self.opt_person_cb.update()
        self.get_person_details_button = Button(self.edit_window, text="Open Person Details", width=20,
                                                command=self.get_details)
        self.get_person_details_button.grid(padx=self.padx, pady=self.pady, row=4, column=0, columnspan=2)

    def destroy_details_gui(self):
        if self.opened_details:
            # hide every old detail input field (in case that we change the chosen person / person_type)
            self.id_label.grid_forget()
            self.id_entry.grid_forget()
            self.name_label.grid_forget()
            self.name_entry.grid_forget()
            self.depart_label.grid_forget()
            self.depart_cb.grid_forget()
            self.update_details_button.grid_forget()
            # update that all the fields for updating details entries are not shown
            self.opened_details = False
            if self.license_label is not None and self.license_label is not None:
                # only doctors has this update label & entry. Destroy them only if they have been created
                self.license_entry.grid_forget()
                self.license_label.grid_forget()

    def destroy_opt_person_gui(self):
        # If opt_person_cb is shown, delete id
        if self.opt_person_cb:
            self.opt_person_cb.grid_forget()
            self.opt_person_cb = False
        # If get_person_details_button is shown, delete id
        if self.get_person_details_button:
            self.get_person_details_button.grid_forget()
            self.get_person_details_button = False

    def get_details(self):
        # mark that there are fields for editing details
        self.opened_details = True
        # design parameter
        padx_details = 10
        # opt_person_cb contains values with this format: "*person id*, *person name*". we need the id, so we use split
        person_id_name = self.opt_person_cb.get()
        person_id = person_id_name.split(", ")[0]
        # save this person_id, in case that it will be changed by the user
        self.curr_person_id = person_id
        person_name = person_id_name.split(", ")[1]
        # get this person's department (we already know his ID and name)
        cursor = self.conn.cursor()
        sql_query = "select dep_name " \
                    "from " + self.table_name +\
                    " inner join departments on dep_id = " + self.person_type + "_department"\
                    " where " + self.person_type + "_id = " + person_id
        cursor.execute(sql_query)
        row = cursor.fetchone()
        person_dep_name = row[0]
        # define GUI elements
        self.id_label = Label(self.edit_window, text='ID: ')
        self.id_label.grid(padx=padx_details, pady=self.pady, row=5, column=0)

        self.id_entry = Entry(self.edit_window)
        self.id_entry.insert(0, person_id)
        self.id_entry.grid(padx=padx_details, pady=self.pady, row=5, column=1)
        self.id_entry.focus_set()

        self.name_label = Label(self.edit_window, text='Name: ')
        self.name_label.grid(padx=padx_details, pady=self.pady, row=6, column=0)

        self.name_entry = Entry(self.edit_window)
        self.name_entry.insert(0, person_name)
        self.name_entry.grid(padx=padx_details, pady=self.pady, row=6, column=1)
        self.name_entry.focus_set()

        self.depart_label = Label(self.edit_window, text='Department: ')
        self.depart_label.grid(padx=padx_details, pady=self.pady, row=7, column=0)

        self.depart_cb = ttk.Combobox(self.edit_window, state='readonly', values=self.departments_names)
        self.depart_cb.current(self.departments_names.index(person_dep_name))
        self.depart_cb.grid(padx=padx_details, pady=self.pady, row=7, column=1)
        self.depart_cb.focus_set()

        if self.person_type == 'Doctor':
            # only doctors has license_no field, therefore only if person_type == 'Doctor' these will be shown
            # get the selected doctor's license_no
            sql_query = "select license_no " \
                        "from doctors " + \
                        "where doctor_id = %s;"
            cursor.execute(sql_query, person_id)
            row = cursor.fetchone()
            license_no = row[0]
            # define GUI elements
            self.license_label = Label(self.edit_window, text='License No.: ')
            self.license_label.grid(padx=padx_details, pady=self.pady, row=8, column=0)

            self.license_entry = Entry(self.edit_window)
            self.license_entry.insert(0, license_no)
            self.license_entry.grid(padx=padx_details, pady=self.pady, row=8, column=1)
            self.license_entry.focus_set()

        self.update_details_button = Button(self.edit_window, text="Update Details", width=20,
                                            command=self.update_details)
        self.update_details_button.grid(padx=self.padx, pady=self.pady, row=9, column=0, columnspan=2)

    def update_details(self):
        # make sure all the data inserted is legal
        if not self.input_validation():
            tkMessageBox.showinfo("Something Went Wrong...", "One or more of the fields are empty / invalid. Make sure"
                                                             " that:\n\n1. The ID has only digits, and its length is 9"
                                                             "\n2. If it is a doctor, make sure license number is 10 "
                                                             "digits\n3. The name has alphabets & spaces only "
                                                             "and its length is more than 5\n\n"
                                                             "Fix the Input, and click the Update Details button "
                                                             "again.")
            return
        # get the inputted details and update the relevant table
        curr_id = self.curr_person_id
        new_id = self.id_entry.get()
        new_name = self.name_entry.get()
        new_dep_name = self.depart_cb.get()
        new_dep_id = self.departments_dict[new_dep_name]

        cursor = self.conn.cursor()
        # only doctors have license_no field, therefore only them needs it to be updated
        if self.person_type == 'Doctor':
            new_license_no = self.license_entry.get()
            sql_query = "update doctors" + \
                        " set doctor_name = %s, "\
                        + "doctor_id = %s, " \
                        + "doctor_department = %s, "\
                        + "license_no = %s "\
                        + " where doctor_id = %s;"
            cursor.execute(sql_query, (new_name, new_id, new_dep_id, new_license_no, curr_id))
        else:
            sql_query = "update " + self.table_name + \
                        " set " + self.person_type + "_name = %s, " \
                        + self.person_type + "_id = %s, " \
                        + self.person_type + "_department = %s" \
                        + " where " + self.person_type + "_id = %s;"
            cursor.execute(sql_query, (new_name, new_id, new_dep_id, curr_id))
        try:
            # put the changes in the DB
            self.conn.commit()
            tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
        except MySQLdb.Error:
            # take care of connection lost or invalid input data (e.g an existing ID)
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number / doctor's "
                                                             "license number might be taken, or connection is lost.")

    def input_validation(self):
        new_id = self.id_entry.get()
        new_name = self.name_entry.get()
        new_license_no = None
        if self.person_type == 'Doctor':
            new_license_no = self.license_entry.get()

        # check that:
        # 1. the ID has only digits, and its length is 9
        # 2. if it is a doctor, make sure license number is 10 digits
        # 3. the name has alphabets and spaces only and its length is more than 5
        if (len(new_id) == 9 and new_id.isdigit()) and \
            (new_license_no is None or (new_license_no.isdigit() and len(new_license_no) == 10)) and \
                (all(x.isalpha() or x.isspace() for x in new_name) and len(new_name) > 5):
            return True
        else:
            return False





