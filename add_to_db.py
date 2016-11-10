import MySQLdb
from Tkinter import *
# import Tkinter
import tkMessageBox
import ttk

class add_doctor_func:
    # connection to the DB
    conn = None
    cursor = None
    # design parameters
    padx = 50
    pady = 10
    # a field for entering a new doctor's id number
    doctor_id_entry = None
    # a field for entering a new doctor's name
    doctor_name_entry = None
    # a field for entering a new doctor's license number
    doctor_license_entry = None
    # choose a departure, from the existing ones in the DB
    doctor_department_cb = None
    # translates department_name to department_id
    departments_dict = None
    # the main editing window
    doctor_window = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open a connection
        self.conn = MySQLdb.connect(db_ip, db_user, db_pass, db_name)
        self.doctor_window = Toplevel()
        img = PhotoImage(file='hospital-icon-20.gif')
        self.doctor_window.tk.call('wm', 'iconphoto', self.doctor_window._w, img)
        self.doctor_window.wm_title("Add new doctor:")
        # get all the departments from the DB
        cursor = self.conn.cursor()
        sql_query = "select * " \
                    "from departments;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()
        # reset a list and a dictionary to map the departments from the DB
        departments_names = []
        self.departments_dict = {}

        for row in result_set:
            # row[0] - dep_id, row[1] - dep_name
            departments_names.append(row[1])
            self.departments_dict[row[1]] = row[0]
        #id
        doctor_id_lable = Label(self.doctor_window, text="id:")
        doctor_id_lable.grid(row=0, column=0)
        self.doctor_id_entry = Entry(self.doctor_window)
        self.doctor_id_entry.grid(padx=self.padx, pady=self.pady, row=0, column=1)
        #name
        doctor_name_lable = Label(self.doctor_window, text="Name:")
        doctor_name_lable.grid(padx=self.padx, pady=self.pady, row=1, column=0)
        self.doctor_name_entry = Entry(self.doctor_window)
        self.doctor_name_entry.grid(padx=self.padx, pady=self.pady, row=1, column=1)
        #License number
        doctor_license_lable = Label(self.doctor_window, text="License number:")
        doctor_license_lable.grid(padx=self.padx, pady=self.pady, row=2, column=0)
        self.doctor_license_entry = Entry(self.doctor_window)
        self.doctor_license_entry.grid(padx=self.padx, pady=self.pady, row=2, column=1)
        #department
        doctor_department_lable = Label(self.doctor_window, text="department:")
        doctor_department_lable.grid(padx=self.padx, pady=self.pady, row=4, column=0)
        self.doctor_department_cb = ttk.Combobox(self.doctor_window, values=departments_names, state='readonly')
        self.doctor_department_cb.grid(padx=self.padx, pady=self.pady, row=4, column=1)

        send_button = Button(self.doctor_window, text="add a doctor ", command=self.send_data, width=15)
        send_button.grid(row=7, column=0)

        self.doctor_window.mainloop()

    def input_validation(self, new_id, new_name, new_license_no):
        # check that:
        # 1. the ID has only digits, and its length is 9
        # 2. if it is a doctor, make sure license number is 10 digits
        # 3. the name has alphabets and spaces only and its length is more than 2
        if (len(new_id) == 9 and new_id.isdigit()) and \
                (new_license_no is None or (new_license_no.isdigit() and len(new_license_no) == 10)) and \
                (all(x.isalpha() or x.isspace() for x in new_name) and len(new_name) > 2):
            return True
        else:
            return False

    # add new doctor to the DB
    def send_data(self):
        self.cursor = self.conn.cursor()
        # get the inputted details
        new_id = self.doctor_id_entry.get()
        new_name = self.doctor_name_entry.get()
        new_license = self.doctor_license_entry.get()
        new_department_name = self.doctor_department_cb.get()
        new_department_id = self.departments_dict[new_department_name]
        #get all the doctors where end_of_treat_date is null or nurse_end_of_employ_date > now()
        doctor_id_query = "select * from doctors where doctor_end_of_employ_date is null or doctor_end_of_employ_date > now();"
        self.cursor.execute(doctor_id_query)
        result = self.cursor.fetchall()
        #list of ids
        doctors_ids = []
        for row in result:
            doctors_ids.append(row[0])
        #check if the new id already exists in DB
        for person in doctors_ids:
            if person == new_id:
                tkMessageBox.showinfo("existing doctor", "This doctor already exists!\nYou can edit this doctor's details\nat the editing wizard")
                self.doctor_window.destroy()
                return
        # make sure all the data inserted is legal
        is_validate = self.input_validation(new_id, new_name, new_license)
        if is_validate==True :
            sql_query = "insert into doctors (doctor_id, doctor_name, license_no, doctor_start_of_employ_date, doctor_department) values(%s, %s, %s, now(), %s);"
            self.cursor.execute(sql_query, (new_id, new_name, new_license, new_department_id))
            try:
                # put the changes in the DB
                self.conn.commit()
                tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
            except MySQLdb.Error:
                # take care of connection lost or invalid input data (e.g an existing ID)
                tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                                 " check your input.\nThe requested ID number / doctor's "
                                                                 "license number might be taken, or connection is lost.")
            self.doctor_window.destroy()
        else:
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number / doctor's "
                                                             "license number might be taken, or connection is lost.")
            self.doctor_window.destroy()

class add_nurse_func:
    # connection to the DB
    conn = None
    cursor = None
    # design parameters
    padx = 50
    pady = 10
    # a field for entering a new doctor's id number
    nurse_id_entry = None
    # a field for entering a new doctor's name
    nurse_name_entry = None
    # choose a departure, from the existing ones in the DB
    nurse_department_cb = None
    # the main editing window
    nurse_window = None
    # translates department_name to department_id
    departments_dict = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open a connection
        self.conn = MySQLdb.connect(db_ip, db_user, db_pass, db_name)
        self.nurse_window = Toplevel()

        img = PhotoImage(file='hospital-icon-20.gif')
        self.nurse_window.tk.call('wm', 'iconphoto', self.nurse_window._w, img)
        self.nurse_window.wm_title("Add new nurse:")

        # get all the departments from the DB
        cursor = self.conn.cursor()

        sql_query = "select * from departments;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()
        # reset a list and a dictionary to map the departments from the DB
        departments_names = []
        self.departments_dict = {}

        for row in result_set:
            # row[0] - dep_id, row[1] - dep_name
            departments_names.append(row[1])
            self.departments_dict[row[1]] = row[0]
        #id
        nurse_id_lable = Label(self.nurse_window, text="id:")
        nurse_id_lable.grid(row=0, column=0)
        self.nurse_id_entry = Entry(self.nurse_window)
        self.nurse_id_entry.grid(padx=self.padx, pady=self.pady, row=0, column=1)
        #name
        nurse_name_lable = Label(self.nurse_window, text="Name:")
        nurse_name_lable.grid(padx=self.padx, pady=self.pady, row=1, column=0)
        self.nurse_name_entry = Entry(self.nurse_window)
        self.nurse_name_entry.grid(padx=self.padx, pady=self.pady, row=1, column=1)
        #department
        nurse_department_lable = Label(self.nurse_window, text="department:")
        nurse_department_lable.grid(padx=self.padx, pady=self.pady, row=4, column=0)
        self.nurse_department_cb = ttk.Combobox(self.nurse_window, values=departments_names, state='readonly')
        self.nurse_department_cb.grid(padx=self.padx, pady=self.pady, row=4, column=1)

        send_button = Button(self.nurse_window, text="add a nurse ", command=self.send_data, width=15)
        send_button.grid(row=7, column=0)

        self.nurse_window.mainloop()

    def input_validation(self, new_id, new_name):
        # check that:
        # 1. the ID has only digits, and its length is 9
        # 2. the name has alphabets and spaces only and its length is more than 2
        if (len(new_id) == 9 and new_id.isdigit()) and \
                (all(x.isalpha() or x.isspace() for x in new_name) and len(new_name) > 2):
            return True
        else:
            return False

    def send_data(self):
        self.cursor = self.conn.cursor()
        # get the inputted details
        new_id = self.nurse_id_entry.get()
        new_name = self.nurse_name_entry.get()
        new_department_name = self.nurse_department_cb.get()
        new_department_id = self.departments_dict[new_department_name]
        #get all the nurses where end_of_treat_date is null or nurse_end_of_employ_date > now()
        nurse_id_query = "select * from nurses where nurse_end_of_employ_date is null or nurse_end_of_employ_date > now();"
        self.cursor.execute(nurse_id_query)
        result = self.cursor.fetchall()
        #list of ids
        nurses_ids = []
        for row in result:
            nurses_ids.append(row[0])
        #check if the new id already exists in DB
        for person in nurses_ids:
            if person == new_id:
                tkMessageBox.showinfo("existing nurse", "This nurse already exists!\nYou can edit this nurse's details\nat the editing wizard")
                self.nurse_window.destroy()
                return
        # make sure all the data inserted is legal
        is_validate = self.input_validation(new_id, new_name)
        if is_validate==True :
            sql_query = "insert into nurses (nurse_id, nurse_name, nurse_start_of_employ_date, nurse_department) values(%s, %s, now(), %s);"
            self.cursor.execute(sql_query, (new_id, new_name, new_department_id))
            try:
                # put the changes in the DB
                self.conn.commit()
                tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
            except MySQLdb.Error:
                # take care of connection lost or invalid input data (e.g an existing ID)
                tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                                 " check your input.\nThe requested ID number / doctor's "
                                                                 "license number might be taken, or connection is lost.")


            self.nurse_window.destroy()
        else:
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number might be taken or connection is lost.")
            self.nurse_window.destroy()

class add_patient_func:
    # connection to the DB
    conn = None
    cursor = None
    # design parameters
    padx = 50
    pady = 10
    #a field for entering a new patient's id number
    patient_id_entry = None
    # a field for entering a new patient's name
    patient_name_entry = None
    # choose a departure, from the existing ones in the DB
    patient_department_cb = None
    # choose a nurse, from the existing ones in the DB
    patient_nurse_cb = None
    # translates department_name to department_id
    departments_dict = None
    # the main editing window
    patient_window = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open a connection
        self.conn = MySQLdb.connect(db_ip, db_user, db_pass, db_name)
        self.patient_window = Toplevel()
        # get all the departments from the DB
        cursor = self.conn.cursor()
        sql_query = "select * " \
                    "from departments;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()
        # reset a list and a dictionary to map the departments from the DB
        departments_names = []
        self.departments_dict = {}

        img = PhotoImage(file='hospital-icon-20.gif')
        self.patient_window.tk.call('wm', 'iconphoto', self.patient_window._w, img)
        self.patient_window.wm_title("Add new nurse:")

        for row in result_set:
            # row[0] - dep_id, row[1] - dep_name
            departments_names.append(row[1])
            self.departments_dict[row[1]] = row[0]

        # get all the nurses from the DB
        sql_query1 = "select * " \
                     "from nurses;"

        cursor.execute(sql_query1)
        result = cursor.fetchall()
        # put all the id and names in a list, separated by ", "
        nurses_names = []
        for row in result:
            nurses_names.append(row[0] + ", " + row[1])

        #id
        patient_id_lable = Label(self.patient_window, text="id:")
        patient_id_lable.grid(row=0, column=0)
        self.patient_id_entry = Entry(self.patient_window)
        self.patient_id_entry.grid(padx=self.padx, pady=self.pady, row=0, column=1)
        #name
        patient_name_lable = Label(self.patient_window, text="Name:")
        patient_name_lable.grid(padx=self.padx, pady=self.pady, row=1, column=0)
        self.patient_name_entry = Entry(self.patient_window)
        self.patient_name_entry.grid(padx=self.padx, pady=self.pady, row=1, column=1)
        #department
        patient_department_lable = Label(self.patient_window, text="department:")
        patient_department_lable.grid(padx=self.padx, pady=self.pady, row=2, column=0)
        self.patient_department_cb = ttk.Combobox(self.patient_window, values=departments_names, state='readonly')
        self.patient_department_cb.grid(padx=self.padx, pady=self.pady, row=2, column=1)
        #treating nurse
        patient_nurse_lable = Label(self.patient_window, text="nurse:")
        patient_nurse_lable.grid(padx=self.padx, pady=self.pady, row=3, column=0)
        self.patient_nurse_cb = ttk.Combobox(self.patient_window, values=nurses_names, state='readonly')
        self.patient_nurse_cb.grid(padx=self.padx, pady=self.pady, row=3, column=1)

        send_button = Button(self.patient_window, text="add a patient ", command=self.send_data, width=15)
        send_button.grid(row=7, column=0)

        self.patient_window.mainloop()


    def input_validation(self, new_id, new_name):
        # check that:
        # 1. the ID has only digits, and its length is 9
        # 2. the name has alphabets and spaces only and its length is more than 2
        if (len(new_id) == 9 and new_id.isdigit()) and \
                (all(x.isalpha() or x.isspace() for x in new_name) and len(new_name) > 2):
            return True
        else:
            return False
    #add new patient to the DB
    def send_data(self):
        self.cursor = self.conn.cursor()
        # get the inputted details
        new_id = self.patient_id_entry.get()
        new_name = self.patient_name_entry.get()
        new_department_name = self.patient_department_cb.get()
        new_department_id = self.departments_dict[new_department_name]
        nurse_name_id = self.patient_nurse_cb.get()
        new_nurses_id = nurse_name_id.split(", ")[0]
        #get all the patients where end_of_treat_date is null
        patients_id_query = "select * from patients where end_of_treat_date is null ;"
        self.cursor.execute(patients_id_query)
        result = self.cursor.fetchall()
        #list of ids
        patients_ids = []
        for row in result:
            patients_ids.append(row[0])
        # check if the new id already exists in DB
        for person in patients_ids:
            if person == new_id:
                tkMessageBox.showinfo("existing patient", "This patient already exists!\nYou can edit this patient's details\nat the editing wizard")
                self.patient_window.destroy()
                return
        # make sure all the data inserted is legal
        is_validate = self.input_validation(new_id,new_name)
        if is_validate==True :
            sql_query = "insert into patients (patient_id, patient_name, start_of_treat_date, patient_department, treating_nurse_id) values(%s, %s, now(), %s, %s);"
            self.cursor.execute(sql_query, (new_id, new_name, new_department_id, new_nurses_id))
            try:
                # put the changes in the DB
                self.conn.commit()
                tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
            except MySQLdb.Error:
                # take care of connection lost or invalid input data (e.g an existing ID)
                tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                                 " check your input.\nThe requested ID number\nor connection is lost.")
            self.patient_window.destroy()
        else:
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number\nor connection is lost.")
class select_person:
    padx = 50
    pady = 10
    window = None
    opt_type_cb = None
    add_button = None
    person_type = None
    db_ip = None
    db_user = None
    db_pass = None
    db_name = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        self.db_ip = db_ip
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.window = Toplevel()
        img = PhotoImage(file='hospital-icon-20.gif')
        self.window.tk.call('wm', 'iconphoto', self.window, img)
        self.window.wm_title("choose window:")
        opt_type_list = ['Doctor', 'Nurse', 'Patient']
        self.opt_type_cb = ttk.Combobox(self.window, state='readonly', values=opt_type_list)
        self.opt_type_cb.current(0)
        self.opt_type_cb.grid(padx=self.padx, pady=self.pady, row=1, column=0, columnspan=2)
        self.add_button = Button(self.window, text="add", width=10, command = self.get_person)
        self.add_button.grid(padx=self.padx, pady=self.pady, row=2, column=0, columnspan=2)

        self.window.mainloop()

    def get_person(self):
        self.person_type = self.opt_type_cb.get()
        if self.person_type == 'Nurse':
            add_nurse_func(self.db_ip, self.db_user, self.db_pass, self.db_name)  # object of new nurse
        elif self.person_type == 'Doctor':
            add_doctor_func(self.db_ip, self.db_user, self.db_pass, self.db_name)#object of new doctor
        elif self.person_type == 'Patient':
            add_patient_func(self.db_ip, self.db_user, self.db_pass, self.db_name)  # object of new patient
        else:
            print "error"


#select_person("localhost", "root", "Polina161", "hospital")