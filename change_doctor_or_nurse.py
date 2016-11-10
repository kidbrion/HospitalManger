import MySQLdb
from Tkinter import *
import ttk
import tkMessageBox



class change_doctor_or_nurse:
    # connection to the DB
    conn = None
    cursor = None
    # choose a patient window
    list_of_patients_window=None
    # choose a patient, from the existing ones in the DB
    choose_patient_cb = None
    # the nurse editing window
    change_window = None
    # choose a nurse, from the existing ones in the DB
    choose_nurse_cb = None
    # choose a doctor, from the existing ones in the DB
    choose_doctor_cb = None
    patient_name = None
    patient_id = None
    patient_department = None
    # choose a doctor, from the existing ones in the DB
    choose_treating_doctor_cb = None
    # the doctor editing window
    change_doctor_window = None


    def __init__(self, db_ip, db_user, db_pass, db_name):
            # open connection for DB
            self.conn = MySQLdb.connect(db_ip, db_user, db_pass, db_name)
            self.list_of_patients_window = Toplevel()
            img = PhotoImage(file='hospital-icon-20.gif')
            self.list_of_patients_window.tk.call('wm', 'iconphoto', self.list_of_patients_window, img)
            self.cursor = self.conn.cursor()
            # get all the patients from the DB
            sql_query = "select * " \
                        "from patients;"

            self.cursor.execute(sql_query)
            result_set = self.cursor.fetchall()
            patients_names = []

            for row in result_set:
                patients_names.append(row[0] + ", " + row[1])

            choose_patient_label = Label(self.list_of_patients_window, text='Choose a patient:')
            choose_patient_label.grid(padx=50, pady=10, row=0, column=0, columnspan=2)

            self.choose_patient_cb = ttk.Combobox(self.list_of_patients_window, state='readonly', values=patients_names)
            self.choose_patient_cb.current(0)
            self.choose_patient_cb.grid(padx=50, pady=10, row=1, column=0, columnspan=2)

            change_nurse_button = Button(self.list_of_patients_window, text="change treating nurse", width=20, command=self.open_nurses)
            change_nurse_button.grid(padx=50, pady=10, row=2, column=0, columnspan=2)

            change_doctor_button = Button(self.list_of_patients_window, text="change treating doctor", width=20, command=self.open_doctors)
            change_doctor_button.grid(padx=50, pady=10, row=2, column=3, columnspan=2)

            self.list_of_patients_window.mainloop()

    def send_nurse_to_db(self):

        nurse_name_id = self.choose_nurse_cb.get()
        nurse_id = nurse_name_id.split(", ")[0]
        nurse_name = nurse_name_id.split(", ")[1]

        change_nurse_query = "update patients set treating_nurse_id = '" + nurse_id + "' where patient_id = '" + self.patient_id + "';"
        self.cursor.execute(change_nurse_query)
        try:
            # put the changes in the DB
            self.conn.commit()
            tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
        except MySQLdb.Error:
            # take care of connection lost or invalid input data (e.g an existing ID)
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number / doctor's "
                                                             "license number might be taken, or connection is lost.")
        self.change_window.destroy()

    def find_pat_dep(self, patient_id):
        dep_query = "select patient_department from patients where patient_id = " + patient_id
        self.cursor.execute(dep_query)
        dep_result = self.cursor.fetchone()
        print dep_result
        return str(dep_result[0])

    #open list of nurses
    def open_nurses(self):
        patient_name_id = self.choose_patient_cb.get()
        self.patient_id = patient_name_id.split(", ")[0]
        self.patient_name = patient_name_id.split(", ")[1]
        self.patient_department = self.find_pat_dep(self.patient_id)

        self.list_of_patients_window.destroy()
        self.change_window=Toplevel()
        img = PhotoImage(file='hospital-icon-20.gif')
        self.change_window.tk.call('wm', 'iconphoto', self.change_window, img)

        nurse_query = "select * " \
                      "from nurses " \
                      "where (nurse_end_of_employ_date is null or nurse_end_of_employ_date > now()) " \
                      "and (nurse_department = " + self.patient_department + ");"
        print nurse_query
        self.cursor.execute(nurse_query)
        nurses_result = self.cursor.fetchall()
        self.nurses_names = []
        # put all the id and names in a list, separated by ", "
        for row in nurses_result:
            self.nurses_names.append(row[0] + ", " + row[1])

        choose_nurse_label = Label(self.change_window, text='Choose a nurse:')
        choose_nurse_label.grid(padx=50, pady=10, row=0, column=0, columnspan=2)

        self.choose_nurse_cb = ttk.Combobox(self.change_window, state='readonly', values=self.nurses_names)
        self.choose_nurse_cb.current(0)
        self.choose_nurse_cb.grid(padx=50, pady=10, row=1, column=0, columnspan=2)

        send_data = Button(self.change_window, text="change", width=20, command=self.send_nurse_to_db)
        send_data.grid(padx=50, pady=10, row=2, column=0, columnspan=2)

    def send_doctor_to_db(self):
        #cur treating doctor
        treating_doctor_name_id = self.choose_treating_doctor_cb.get()
        doctor_id = treating_doctor_name_id.split(", ")[0]
        doctor_name = treating_doctor_name_id.split(", ")[1]
        #new treating doctor
        new_treating_doctor_name_id = self.choose_doctor_cb.get()
        new_doctor_id = new_treating_doctor_name_id.split(", ")[0]
        new_doctor_name = new_treating_doctor_name_id.split(", ")[1]
        #update new doctor in the DB
        sql_query = "update doctors_patients set doctor_id = '" + new_doctor_id + \
                    "' where pat_id = '" + self.patient_id + "' and doctor_id = '" + doctor_id + "';"

        self.cursor.execute(sql_query)
        try:
            # put the changes in the DB
            self.conn.commit()
            tkMessageBox.showinfo("Mission Complete", "Details Has Been Updated!")
        except MySQLdb.Error:
            # take care of connection lost or invalid input data (e.g an existing ID)
            tkMessageBox.showinfo("Something Went Wrong...", "There was an error updating the data you asked.\nPlease"
                                                             " check your input.\nThe requested ID number / doctor's "
                                                             "license number might be taken, or connection is lost.")
        self.change_doctor_window.destroy()

    def open_doctors(self):
        patient_name_id = self.choose_patient_cb.get()
        self.patient_id = patient_name_id.split(", ")[0]
        self.patient_name = patient_name_id.split(", ")[1]
        self.patient_department = self.find_pat_dep(self.patient_id)

        #get all the doctors from DB
        doctor_query = "select * " \
                       "from doctors " \
                       "where (doctor_end_of_employ_date is null or doctor_end_of_employ_date > now()) " \
                       "and (doctor_department = " + self.patient_department + ");"

        print doctor_query
        self.cursor.execute(doctor_query)
        doctors_result = self.cursor.fetchall()
        doctors_names = []
        # put all the id and names in a list, separated by ", "
        for row in doctors_result:
            doctors_names.append(row[0] + ", " + row[1])
        #get treating doctor name and treating doctor id
        doctors_patients_query = "select doctors_patients.doctor_id, doctors.doctor_name " \
                                 "from doctors_patients inner join doctors " \
                                 "on doctors.doctor_id = doctors_patients.doctor_id " \
                                 "where pat_id = " + self.patient_id + ";"

        self.cursor.execute(doctors_patients_query)
        #if there is no treaing doctors
        if self.cursor.rowcount == 0:
            tkMessageBox.showinfo("No Doctors", "This patients has no treating doctors")
            return

        self.list_of_patients_window.destroy()
        self.change_doctor_window = Toplevel()
        img = PhotoImage(file='hospital-icon-20.gif')
        self.change_doctor_window.tk.call('wm', 'iconphoto', self.change_doctor_window, img)
        #list of treating doctors
        doctors_patients_result = self.cursor.fetchall()
        doctors_patients_names_ids = []
        # put all the id and names in a list, separated by ", "
        for row in doctors_patients_result:
            doctors_patients_names_ids.append(row[0] + ", " + row[1])

        print doctors_patients_names_ids
        choose_doctor_label = Label(self.change_doctor_window, text='Choose a new treating doctor:')
        choose_doctor_label.grid(padx=50, pady=10, row=0, column=3, columnspan=2)

        self.choose_doctor_cb = ttk.Combobox(self.change_doctor_window, state='readonly', values=doctors_names)
        self.choose_doctor_cb.current(0)
        self.choose_doctor_cb.grid(padx=50, pady=10, row=1, column=3, columnspan=2)

        choose_treating_doctor_label = Label(self.change_doctor_window, text='Choose a doctor to replace:')
        choose_treating_doctor_label.grid(padx=50, pady=10, row=0, column=0, columnspan=2)

        self.choose_treating_doctor_cb = ttk.Combobox(self.change_doctor_window, state='readonly', values=doctors_patients_names_ids)
        self.choose_treating_doctor_cb.current(0)
        self.choose_treating_doctor_cb.grid(padx=50, pady=10, row=1, column=0, columnspan=2)

        new_doctor_button = Button(self.change_doctor_window, text="change", width=20, command=self.send_doctor_to_db)
        new_doctor_button.grid(padx=50, pady=10, row=2, column=0, columnspan=2)

