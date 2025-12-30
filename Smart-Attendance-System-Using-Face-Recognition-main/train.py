from tkinter import *
from PIL import Image, ImageTk
import os, cv2, numpy as np
from tkinter import messagebox

class Train:

    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.root.title("Attendance Management System - Train Data")

        # ===== HEADER IMAGE =====
        header_path = r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\data_img\std1.jpg.png"
        if not os.path.exists(header_path):
            messagebox.showerror("Error", f"Header image not found at:\n{header_path}")
            return

        header = Image.open(header_path)
        header = header.resize((1280, 130), Image.LANCZOS)
        self.header_img = ImageTk.PhotoImage(header)
        Label(self.root, image=self.header_img).place(x=0, y=0, width=1280, height=130)

        # ===== BACKGROUND IMAGE =====
        bg_path = r"C:\Users\Simran Dhiman\Downloads\Smart-Attendance-System-Using-Face-Recognition-main\Smart-Attendance-System-Using-Face-Recognition-main\data_img\bg.jpg"
        if not os.path.exists(bg_path):
            messagebox.showerror("Error", f"Background image not found at:\n{bg_path}")
            return

        bg = Image.open(bg_path)
        bg = bg.resize((1280, 620), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)
        bg_label = Label(self.root, image=self.bg_img)
        bg_label.place(x=0, y=130, width=1280, height=620)

        # ===== TITLE =====
        Label(bg_label,
              text="TRAIN FACE DATA",
              font=("Verdana", 22, "bold"),
              bg="navyblue",
              fg="white").place(x=0, y=0, width=1280, height=50)

        # ===== TRAIN BUTTON =====
        Button(bg_label,
               text="START TRAINING",
               command=self.train_classifier,
               font=("Tahoma", 16, "bold"),
               bg="white",
               fg="navyblue",
               cursor="hand2").place(x=500, y=300, width=280, height=60)

    # ===== TRAINING FUNCTION =====
    def train_classifier(self):
        data_dir = r"C:\Faces_img"

        if not os.path.exists(data_dir):
            messagebox.showerror("Error", f"Data folder not found:\n{data_dir}")
            return

        faces = []
        ids = []

        # Only process images starting with "user."
        image_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith("user.")]
        if len(image_paths) == 0:
            messagebox.showerror("Error", "No valid face images found! Use filenames like user.<id>.<imageno>.jpg")
            return

        try:
            for image_path in image_paths:
                img = Image.open(image_path).convert('L')
                image_np = np.array(img, 'uint8')

                # Extract ID from filename
                filename = os.path.split(image_path)[1]  # e.g., user.1.2.jpg
                try:
                    id = int(filename.split('.')[1])
                except:
                    continue  # skip any incorrectly named files

                faces.append(image_np)
                ids.append(id)

                cv2.imshow("Training Images", image_np)
                cv2.waitKey(1)

            ids = np.array(ids)

            # ===== Train LBPH Classifier =====
            clf = cv2.face.LBPHFaceRecognizer_create()
            clf.train(faces, ids)
            clf.write("clf.xml")

            cv2.destroyAllWindows()
            messagebox.showinfo("Success", "Training Completed Successfully!")

        except Exception as e:
            cv2.destroyAllWindows()
            messagebox.showerror("Error", f"Training Failed!\n{str(e)}")


if __name__ == "__main__":
    root = Tk()
    Train(root)
    root.mainloop()
