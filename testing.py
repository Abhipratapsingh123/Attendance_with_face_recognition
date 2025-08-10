import cv2
import pandas as pd
import os
import sys
import csv
import yagmail
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load .env file

SENDER_EMAIL = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# sending email function


def send_email(receiver_email, student_name, teacher_name, subject, date):
    subject = "Attendance Marked Successfully"
    content = f"""
    Hello {student_name},
    
    Your attendance has been successfully marked.
    
    - Date: {date}
    - Teacher: {teacher_name}
    - Subject: {subject}
    - Status: Present
    
    Regards,
    Face Recognition Attendance System
    """
    try:
        yag = yagmail.SMTP(user=SENDER_EMAIL, password=EMAIL_PASSWORD)
        yag.send(to=receiver_email, subject=subject, contents=content)
        print(f"Confirmation email sent to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email to {receiver_email}. Error: {e}")


# Load the face detector and recognizer
face_detector = cv2.CascadeClassifier(
    "/workspaces/Attendance_with_face_recognition/models/haarcascade_frontalface_default.xml")
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read(
    "/workspaces/Attendance_with_face_recognition/models/lbph_classifier.yml")

# Get the teacher's name from command-line arguments
if len(sys.argv) < 3:
    print("Error: Teacher name and subject not provided.")
    sys.exit(1)

teacher_name = sys.argv[1]
subject = sys.argv[2]

# Get the current date and day
current_date = datetime.now().strftime("%Y-%m-%d")
current_day = datetime.now().strftime("%A")

# Define the database folder and ensure it exists
database_folder = "database"
os.makedirs(database_folder, exist_ok=True)

# Define the file path for storing attendance
attendance_file = attendance_file = os.path.join(
    database_folder, f"attendance_{current_date}.xlsx")

# Load existing attendance data if the file exists
if os.path.exists(attendance_file):
    df_existing = pd.read_excel(attendance_file)
else:
    df_existing = pd.DataFrame(
        columns=["Date", "Day", "Teacher", "Subject", "Student Name", "Status"])


# Load registered users from CSV file
user_data_file = "/workspaces/Attendance_with_face_recognition/database/users.csv"
user_dict = {}
email_dict = {}

if os.path.exists(user_data_file):
    with open(user_data_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:  # Ensure the row has at least three values
                try:
                    user_dict[int(row[0])] = row[1]
                    email_dict[int(row[0])] = row[2]
                except ValueError:
                    # Handle non-numeric IDs
                    print(f"Skipping invalid row: {row}")


print(f"Loaded Users: {user_dict}")


# Start video capture
camera = cv2.VideoCapture(0)

# Set dimensions and font
width, height = 220, 220
font = cv2.FONT_HERSHEY_COMPLEX_SMALL

attendance_data = []
# Prevent duplicate attendance
marked_students = set(df_existing["Student Name"].unique())

recognition_delay = 8  # frames to hold after detection
hold_frames = 0
while True:
    connected, image = camera.read()
    if not connected:
        break

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detections = face_detector.detectMultiScale(
        image_gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(30, 30)
    )

    for (x, y, w, h) in detections:
        image_face = cv2.resize(image_gray[y:y + h, x:x + w], (width, height))
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        id, confidence = face_recognizer.predict(image_face)
        if confidence < 55 or confidence >= 95:
            name = "Unknown"

        else:
            name = user_dict.get(id, "Unknown")
            email = email_dict.get(id, "")

        cv2.putText(image, f"Name: {name}",
                    (x, y + h + 30), font, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Confidence: {round(confidence, 2)}",
                    (x, y + h + 60), font, 1, (0, 255, 0), 2)

        if confidence >= 61 and name != "Unknown" and name not in marked_students:
            attendance_data.append(
                [current_date, current_day, teacher_name, subject, name, "P"])
            marked_students.add(name)
            print(
                f"Attendance marked for {name} (Confidence: {confidence:.2f})")
            if email:
                send_email(email, name, teacher_name, subject, current_date)
            hold_frames = recognition_delay

        elif name in marked_students:
            cv2.putText(image, "Already Marked, Press Q", (x, y + h + 90),
                        font, 1, (0, 255, 0), 2)

        if confidence < 55 or confidence >= 95:
            # Show the message for low confidence detection
            cv2.putText(image, "Face not recognized.", (x, y + h + 120),
                        font, 1, (0, 0, 255), 1)

    if hold_frames > 0:
        hold_frames -= 1
    # else:
    #     if len(attendance_data) > 0:  # Someone was recognized
    #         break  # Exit loop after the delay

    cv2.imshow("Face Recognition", image)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Release camera and close window
camera.release()
cv2.destroyAllWindows()

# Convert existing data into a dictionary (Student Name -> Index mapping)
existing_status = dict(zip(df_existing['Student Name'], df_existing['Status']))

# Add absent students
for student_id, student_name in user_dict.items():
    if student_name not in marked_students:
        # If already marked Present in existing file, don't overwrite
        if existing_status.get(student_name) != "P":
            attendance_data.append(
                [current_date, current_day, teacher_name, subject, student_name, "A"])

# Append new attendance data to the existing file
df_new = pd.DataFrame(attendance_data, columns=[
                      "Date", "Day", "Teacher", "Subject", "Student Name", "Status"])
df_final = pd.concat([df_existing, df_new], ignore_index=True)
df_final.to_excel(attendance_file, index=False)

print(f"Attendance saved successfully in {attendance_file}")
