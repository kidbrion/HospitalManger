#!/usr/bin/python
import MySQLdb
from Tkinter import *
import ttk
import tkMessageBox


class RemovePersonGUI:
    # This GUI allows the user to delete doctor / patient / nurse

    # connection to the DB
    conn = None
    # the chosen option from opt_type_list which contains doctor / patient / nurse
    person_type = None
    # the table to select from in queries
    table_name = None
    # end of relevancy to the system date, varies between the different person types
    end_date_col = None
    # GUI Parameters:
    # the main editing window
    remove_window = None
    # design parameters
    padx = 50
    pady = 10
    # ComboBoxes in use:
    # choose doctor / patient / nurse
    opt_type_cb = None
    # choose the person to delete, from the existing ones in the DB. The false value is in order to mark that this is
    # the first time opt_person_cb is shown
    opt_person_cb = False
    # Labels in use:
    choose_type_label = None
    # Buttons in use:
    delete_button = None

    def __init__(self, db_ip, db_user, db_pass, db_name):
        # open a connection
        self.conn = MySQLdb.connect(host=db_ip, user=db_user, passwd=db_pass, db=db_name)
        self.remove_window = Toplevel()
        # set window icon
        img = PhotoImage(file='hospital-icon-20.gif')
        self.remove_window.tk.call('wm', 'iconphoto', self.remove_window._w, img)
        self.remove_window.wm_title("Delete Person From the System")

        self.choose_type_label = Label(self.remove_window, text='Edit a:')
        self.choose_type_label.grid(padx=self.padx, pady=self.pady, row=0, column=0, columnspan=2)

        opt_type_list = ['Doctor', 'Nurse', 'Patient']
        self.opt_type_cb = ttk.Combobox(self.remove_window, state='readonly', values=opt_type_list)
        self.opt_type_cb.current(0)
        self.opt_type_cb.grid(padx=self.padx, pady=self.pady, row=1, column=0, columnspan=2)

        get_persons_button = Button(self.remove_window, text="Open Selection", width=20, command=self.get_person_opt)
        get_persons_button.grid(padx=self.padx, pady=self.pady, row=2, column=0, columnspan=2)

        self.remove_window.mainloop()

    def get_person_opt(self):
        cursor = self.conn.cursor()
        self.person_type = self.opt_type_cb.get()
        # all the person types match the DB's table names, with an 'S' in the end
        self.table_name = self.person_type + "s"
        # reset a list for all the people from this person type on the DB
        person_opt_names = []
        if self.person_type == 'Patient':
            self.end_date_col = "end_of_treat_date"
        else:
            self.end_date_col = self.person_type + "_end_of_employ_date"
        # get name & id of each person matching the chosen type, which is still relevant (the end date is NULL).
        # each field in the tables nurses, doctors and patients is in this format:
        # *person type*_*field info* (e.g. patient_id and doctor_id)
        sql_query = "select " + self.person_type + "_id,  " + self.person_type + "_name " \
                    "from " + self.table_name + \
                    " where " + self.end_date_col + " is NULL or " + self.end_date_col + " > now() " \
                    " order by " + self.person_type + "_name;"
        cursor.execute(sql_query)
        result_set = cursor.fetchall()

        if cursor.rowcount == 0:
            self.destroy_opt_person_gui()
            tkMessageBox.showinfo("Something Went Wrong...", "No available " + self.table_name.lower())
            return

        # put all the id and names in a list, separated by ", "
        for row in result_set:
            person_opt_names.append(row[0] + ", " + row[1])
        # opt_person_cb = False means it is the first time this combobox is shown, therefore there is no need to update
        # it, in case that the user has chosen another option from opt_type_cb
        if not self.opt_person_cb:
            self.opt_person_cb = ttk.Combobox(self.remove_window, state='readonly', values=person_opt_names)
            self.opt_person_cb.current(0)
            self.opt_person_cb.grid(padx=self.padx, pady=self.pady, row=3, column=0, columnspan=2)
        else:
            # update the person_opt_names to select from
            self.opt_person_cb['values'] = person_opt_names
            self.opt_person_cb['state'] = 'readonly'
            self.opt_person_cb.current(0)
            self.opt_person_cb.update()
        self.delete_button = Button(self.remove_window, text="Delete", width=20,
                                    command=self.delete_person)
        self.delete_button.grid(padx=self.padx, pady=self.pady, row=4, column=0, columnspan=2)

    def destroy_opt_person_gui(self):
        # If opt_person_cb is shown, delete id
        if self.opt_person_cb:
            self.opt_person_cb.grid_forget()
            self.opt_person_cb = False
        # If delete_button is shown, delete id
        if self.delete_button:
            self.delete_button.grid_forget()
            self.delete_button = False

    def delete_person(self):
        # make sure that is the user's will
        result = tkMessageBox.askquestion("Delete", "Are you sure you want to delete " + self.opt_person_cb.get() + "?",
                                          icon='warning')
        if result == 'no':
            return
        # opt_person_cb contains values with this format: "*person id*, *person name*". we need the id, so we use split
        person_id_name = self.opt_person_cb.get()
        person_id = person_id_name.split(", ")[0]

        cursor = self.conn.cursor()
        # check if there is a problem to delete this person. Each person type might have different issues
        if self.person_type == 'Nurse':
            # a nurse can be deleted if she has any patients she is currently taking care of
            # check if there are patients that this nurse takes care of
            sql_query = "select patient_id from patients where treating_nurse_id = '" + person_id + "'" \
                        "and end_of_treat_date is NULL or end_of_treat_date > now();"
            cursor.execute(sql_query)
            result_set = cursor.fetchall()

            if cursor.rowcount != 0:
                # there are patients this nurse takes care of
                err_msg = "The nurse: " + person_id_name +\
                          " has one or more patients to take care of. \nDelete these or update" \
                          " their treating nurse first. \nThe patients IDs: "
                # list all the patients this nurse takes care of:
                for row in result_set:
                    err_msg += row[0] + " "

                tkMessageBox.showinfo("Something Went Wrong...", err_msg)
                return

        if self.person_type == 'Doctor':
            # a doctor can be deleted only if all his patients has more than one doctor treating except them
            # check if this doctor is the only doctor of a patient, with SQL count function
            sql_query = "select a.pat_id " + \
                        "from (" \
                        "select pat_id, doctor_id, count(doctor_id) as num_of_docs " \
                        "from doctors_patients " \
                        "group by pat_id" \
                        ") as a " \
                        "where a.doctor_id = '" + person_id + "' and a.num_of_docs = 1"
            cursor.execute(sql_query)
            result_set = cursor.fetchall()

            if cursor.rowcount != 0:
                # there is a patient this doctor is the only one to take care of
                err_msg = "The doctor: " + person_id_name + \
                          " has one or more patients that he is their only doctor.\n" \
                          "A patient must have at least one doctor that takes care of him/her." \
                          "\nThese patients IDs: "
                # display these patients on err_msg
                for row in result_set:
                    err_msg += row[0] + " "

                tkMessageBox.showinfo("Something Went Wrong...", err_msg)
                return

            else:
                # this doctor can be deleted. Remove it from doctors_patients table
                sql_query = "delete from doctors_patients where doctor_id = '" + person_id + "';"
                cursor.execute(sql_query)

        else:
            # it is a patient. Remove it from doctors_patients table
            sql_query = "delete from doctors_patients where pat_id = '" + person_id + "';"
            cursor.execute(sql_query)

        # execute the deletion - make this person irrelevant for the system by their end date
        sql_query = "update " + self.table_name + " set " + self.end_date_col + " = now() " \
                    " where " + self.person_type + "_id = '" + person_id + "';"

        cursor.execute(sql_query)
        try:
            # put the changes in the DB
            self.conn.commit()
            tkMessageBox.showinfo("Mission Complete", "This " + self.person_type.lower() + " has been deleted.")
            self.destroy_opt_person_gui()
        except MySQLdb.Error:
            # take care of connection lost
            tkMessageBox.showinfo("Something Went Wrong...",
                                  "Please Try Again...")


#RemovePersonGUI('hospital', '1056', 'root', 'localhost')






