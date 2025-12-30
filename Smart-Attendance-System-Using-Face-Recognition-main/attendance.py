import os
import csv
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime

# Global variable for CSV data
mydata = []

class Attendance:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance Management System using Facial Recognition")
        self.root.state("zoomed")

        # ============== Variables ==============
        self.var_id = StringVar()
        self.var_roll = StringVar()
        self.var_name = StringVar()
        self.var_time = StringVar()
        self.var_date = StringVar()
        self.var_attend = StringVar(value="Status")

        # ============== Header Image ==============
        try:
            img = Image.open("Smart-Attendance-System-Using-Face-Recognition-main/Screenshot 2025-10-11 182117.png")
            img = img.resize((1280, 130), Image.LANCZOS)
            self.photoimg = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error loading header image:", e)
            self.photoimg = None

        if self.photoimg:
            f_lb1 = Label(self.root, image=self.photoimg)
            f_lb1.place(x=0, y=0, width=1280, height=130)

        # ============== Background Frame ==============
        bg_img = Frame(self.root, bg="lightgray")
        bg_img.place(x=0, y=145, width=1280, height=500)

        # Title
        title_lb1 = Label(bg_img, text="Attendance Management", font=("verdana", 20, "bold"),
                          bg="navyblue", fg="white")
        title_lb1.place(x=0, y=0, width=1280, height=40)

        # Main Frame
        main_frame = Frame(bg_img, bd=2, bg="white")
        main_frame.place(x=0, y=40, width=1280, height=450)

        # ============== Left Frame (Student Data) ==============
        left_frame = LabelFrame(main_frame, bd=2, bg="white", relief=RIDGE, text="Student",
                                font=("verdana", 12, "bold"), fg="navyblue")
        left_frame.place(x=10, y=10, width=640, height=430)

        # Labels and Entry Fields
        Label(left_frame, text="Student ID:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_id, width=15, font=("verdana", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)

        Label(left_frame, text="Roll No:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_roll, width=15, font=("verdana", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)

        Label(left_frame, text="Name:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_name, width=15, font=("verdana", 12, "bold")).grid(row=1, column=1, padx=5, pady=5)

        Label(left_frame, text="Time:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_time, width=15, font=("verdana", 12, "bold")).grid(row=1, column=3, padx=5, pady=5)

        Label(left_frame, text="Date:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_date, width=15, font=("verdana", 12, "bold")).grid(row=2, column=1, padx=5, pady=5)

        Label(left_frame, text="Status:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        attend_combo = ttk.Combobox(left_frame, textvariable=self.var_attend, width=13, font=("verdana", 12, "bold"), state="readonly")
        attend_combo["values"] = ("present", "absent")
        attend_combo.current(0)
        attend_combo.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        # ============== Left Table (CSV) ==============
        table_frame = Frame(left_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=10, y=100, width=615, height=280)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)
        self.attendanceReport_left = ttk.Treeview(table_frame,
                                                  columns=("ID", "Roll_No", "Name", "Time", "Date", "Attend"),
                                                  xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.attendanceReport_left.xview)
        scroll_y.config(command=self.attendanceReport_left.yview)

        for col, width in zip(("ID", "Roll_No", "Name", "Time", "Date", "Attend"), (50, 70, 100, 70, 70, 80)):
            self.attendanceReport_left.heading(col, text=col)
            self.attendanceReport_left.column(col, width=width)
        self.attendanceReport_left["show"] = "headings"
        self.attendanceReport_left.pack(fill=BOTH, expand=1)
        self.attendanceReport_left.bind("<ButtonRelease>", self.get_cursor_left)

        # Buttons
        btn_frame = Frame(left_frame, bg="white")
        btn_frame.place(x=10, y=385, width=615, height=40)
        Button(btn_frame, text="Import CSV", command=self.importCsv, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Export CSV", command=self.exportCsv, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).grid(row=0, column=1, padx=5)
        Button(btn_frame, text="Update", command=self.action, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).grid(row=0, column=2, padx=5)
        Button(btn_frame, text="Reset", command=self.reset_data, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).grid(row=0, column=3, padx=5)

        # ============== Right Frame (MySQL Table) ==============
        right_frame = LabelFrame(main_frame, bd=2, bg="white", relief=RIDGE, text="Database Records",
                                 font=("verdana", 12, "bold"), fg="navyblue")
        right_frame.place(x=660, y=10, width=600, height=430)

        table_frame = Frame(right_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=10, y=70, width=580, height=350)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)
        self.attendanceReport = ttk.Treeview(table_frame,
                                             columns=("ID", "Roll_No", "Name", "Time", "Date", "Attend"),
                                             xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.attendanceReport.xview)
        scroll_y.config(command=self.attendanceReport.yview)

        for col, width in zip(("ID", "Roll_No", "Name", "Time", "Date", "Attend"), (50, 70, 100, 70, 70, 80)):
            self.attendanceReport.heading(col, text=col)
            self.attendanceReport.column(col, width=width)
        self.attendanceReport["show"] = "headings"
        self.attendanceReport.pack(fill=BOTH, expand=1)
        self.attendanceReport.bind("<ButtonRelease>", self.get_cursor_right)

        Button(right_frame, text="Edit", command=self.update_data, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).place(x=10, y=10)
        Button(right_frame, text="Delete", command=self.delete_data, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).place(x=130, y=10)

        # Fetch data from database
        self.fetch_data()

    # ===================== CSV Import/Export =====================
    def fetchData(self, rows):
        global mydata
        mydata = rows
        self.attendanceReport_left.delete(*self.attendanceReport_left.get_children())
        for i in rows:
            self.attendanceReport_left.insert("", END, values=i)

    def importCsv(self):
        mydata.clear()
        fln = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open CSV",
                                         filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
        if fln:
            with open(fln) as myfile:
                csvread = csv.reader(myfile, delimiter=",")
                for i in csvread:
                    mydata.append(i)
            self.fetchData(mydata)

    def exportCsv(self):
        try:
            if len(mydata) < 1:
                messagebox.showerror("Error", "No Data Found!", parent=self.root)
                return
            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save CSV",
                                               filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
            if fln:
                with open(fln, mode="w", newline="") as myfile:
                    exp_write = csv.writer(myfile, delimiter=",")
                    for i in mydata:
                        exp_write.writerow(i)
                messagebox.showinfo("Success", "Data exported successfully!", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)

    # ===================== Cursor Functions =====================
    def get_cursor_left(self, event=""):
        cursor_focus = self.attendanceReport_left.focus()
        content = self.attendanceReport_left.item(cursor_focus)
        data = content.get("values", [])
        if data:
            self.var_id.set(data[0])
            self.var_roll.set(data[1])
            self.var_name.set(data[2])
            self.var_time.set(data[3])
            self.var_date.set(data[4])
            self.var_attend.set(data[5])

    def get_cursor_right(self, event=""):
        cursor_focus = self.attendanceReport.focus()
        content = self.attendanceReport.item(cursor_focus)
        data = content.get("values", [])
        if data:
            self.var_id.set(data[0])
            self.var_roll.set(data[1])
            self.var_name.set(data[2])
            self.var_time.set(data[3])
            self.var_date.set(data[4])
            self.var_attend.set(data[5])

    # ===================== Reset Data =====================
    def reset_data(self):
        self.var_id.set("")
        self.var_roll.set("")
        self.var_name.set("")
        self.var_time.set("")
        self.var_date.set("")
        self.var_attend.set("Status")

    # ===================== Database Actions =====================
    def fetch_data(self):
        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                           database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM stdattendance")
            data = mycursor.fetchall()
            if data:
                self.attendanceReport.delete(*self.attendanceReport.get_children())
                for row in data:
                    self.attendanceReport.insert("", END, values=row)
            conn.close()
        except Exception as es:
            messagebox.showerror("Error", f"Database fetch error: {str(es)}", parent=self.root)

    def action(self):
        if (self.var_id.get() == "" or self.var_roll.get() == "" or self.var_name.get() == "" or
            self.var_time.get() == "" or self.var_date.get() == "" or self.var_attend.get() == ""):
            messagebox.showerror("Error", "Please fill in all required fields!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("INSERT INTO stdattendance (std_id,std_roll_no,std_name,std_time,std_date,std_attendance) VALUES (%s,%s,%s,%s,%s,%s)",
                                 (self.var_id.get(), self.var_roll.get(), self.var_name.get(), self.var_time.get(),
                                  self.var_date.get(), self.var_attend.get()))
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success", "Record added successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database insert error: {str(es)}", parent=self.root)

    def update_data(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Please select a record to update!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute(
                    "UPDATE stdattendance SET std_roll_no=%s,std_name=%s,std_time=%s,std_date=%s,std_attendance=%s WHERE std_id=%s",
                    (self.var_roll.get(), self.var_name.get(), self.var_time.get(), self.var_date.get(),
                     self.var_attend.get(), self.var_id.get()))
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success", "Record updated successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database update error: {str(es)}", parent=self.root)

    def delete_data(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Please select a record to delete!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("DELETE FROM stdattendance WHERE std_id=%s", (self.var_id.get(),))
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success", "Record deleted successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database delete error: {str(es)}", parent=self.root)

# ===================== Example of opening Attendance window from main app =====================
if __name__ == "__main__":
    root = Tk()
    app = Attendance(root)
    root.mainloop()
