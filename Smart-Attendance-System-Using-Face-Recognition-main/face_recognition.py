import mysql.connector
import os
import cv2
import numpy as np
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

class Face_Recognition:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Attendance Management System - Face Recognition")

        # ================= HEADER IMAGE =================
        img = Image.open(r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\data_img\std1.png")
        img = img.resize((1280, 130), Image.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        Label(self.root, image=self.photoimg).place(x=0, y=0, width=1280, height=130)

        # ================= BACKGROUND IMAGE =================
        bg1 = Image.open(r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\data_img\bg.jpg")
        bg1 = bg1.resize((1280, 520), Image.LANCZOS)
        self.photobg1 = ImageTk.PhotoImage(bg1)
        bg_label = Label(self.root, image=self.photobg1)
        bg_label.place(x=0, y=130, width=1280, height=520)

        # ================= TITLE =================
        Label(bg_label, text="FACE RECOGNITION SYSTEM", font=("Verdana", 22, "bold"),
              bg="navyblue", fg="white").place(x=0, y=0, width=1280, height=50)

        # ================= RECOGNITION BUTTON =================
        Button(bg_label, text="START FACE RECOGNITION", command=self.face_recog,
               font=("Tahoma", 16, "bold"), bg="white", fg="navyblue", cursor="hand2").place(x=500, y=300, width=280, height=60)

    # ================= MARK ATTENDANCE =================
    def mark_attendance(self, id, roll_no, name):
        """Marks attendance in attendance.csv if not already marked today."""
        date_str = datetime.now().strftime("%d/%m/%Y")
        time_str = datetime.now().strftime("%H:%M:%S")

        # Create file if doesn't exist
        if not os.path.exists("attendance.csv"):
            with open("attendance.csv", "w") as f:
                f.write("ID,Roll_No,Name,Time,Date,Status\n")

        with open("attendance.csv", "r+", newline="\n") as f:
            data = f.readlines()
            ids_today = [line.split(",")[0] for line in data if line.strip().endswith(date_str)]
            if id not in ids_today:
                f.writelines(f"{id},{roll_no},{name},{time_str},{date_str},Present\n")

    # ================= FACE RECOGNITION FUNCTION =================
    def face_recog(self):
        # Load face classifier and trained model
        faceCascade = cv2.CascadeClassifier(r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read(r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\clf.xml")  # Ensure you have trained clf.xml

        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, clf):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
            coords = []
            for (x, y, w, h) in features:
                cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
                id_, predict = clf.predict(gray_img[y:y+h, x:x+w])
                confidence = int(100 * (1 - predict / 300))

                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost', database='face_recognizer', port=3306)
                cursor = conn.cursor()

                cursor.execute(f"SELECT name, roll_no FROM student WHERE id='{id_}'")
                result = cursor.fetchone()

                if result:
                    name, roll_no = result
                else:
                    name, roll_no = "Unknown", "Unknown"

                if confidence > 77:
                    cv2.putText(img, f"Name: {name}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                    cv2.putText(img, f"Roll: {roll_no}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                    if name != "Unknown":
                        self.mark_attendance(str(id_), roll_no, name)
                else:
                    cv2.putText(img, "Unknown Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

                coords = [x, y, w, h]
            return coords

        def recognize(img, clf, faceCascade):
            draw_boundary(img, faceCascade, 1.1, 10, (255,0,0), clf)
            return img

        cap = cv2.VideoCapture(0)  # Use webcam
        while True:
            ret, img = cap.read()
            if not ret:
                break
            img = recognize(img, clf, faceCascade)
            cv2.imshow("Face Recognition", img)

            if cv2.waitKey(1) & 0xFF == 13:  # Press Enter to exit
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition(root)
    root.mainloop()
