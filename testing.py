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
def send_email(receiver_email, student_name, teacher_name, date):
    subject = "Attendance Marked Successfully"
    content = f"""
    Hello {student_name},
    
    Your attendance has been successfully marked.
    
    - Date: {date}
    - Teacher: {teacher_name}
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
face_detector = cv2.CascadeClassifier("C:\\Users\\abhip\\Desktop\\Minor-Project\\models\\haarcascade_frontalface_default.xml")
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read("C://Users//abhip//Desktop//Minor-Project//models//lbph_classifier.yml")

# Get the teacher's name from command-line arguments
if len(sys.argv) < 2:
    print("Error: Teacher name not provided.")
    sys.exit(1)

teacher_name = sys.argv[1]

# Get the current date and day
current_date = datetime.now().strftime("%Y-%m-%d")
current_day = datetime.now().strftime("%A")

# Define the database folder and ensure it exists
database_folder = "database"
os.makedirs(database_folder, exist_ok=True)

# Define the file path for storing attendance
attendance_file = os.path.join(database_folder, "attendance.xlsx")

# Load existing attendance data if the file exists
if os.path.exists(attendance_file):
    df_existing = pd.read_excel(attendance_file)
else:
    df_existing = pd.DataFrame(columns=["Date", "Day", "Teacher", "Student Name", "Status"])


# Load registered users from CSV file
user_data_file = "C:\\Users\\abhip\\Desktop\\Minor-Project\\database\\users.csv"
user_dict = {}
email_dict = {}

if os.path.exists(user_data_file):
    with open(user_data_file, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 3:  # Ensure the row has at least two values
                try:
                    user_dict[int(row[0])] = row[1]
                    email_dict[int(row[0])] = row[2]
                except ValueError:
                    print(f"Skipping invalid row: {row}")  # Handle non-numeric IDs
            
                
print(f"Loaded Users: {user_dict}")


# Start video capture
camera = cv2.VideoCapture(0)

# Set dimensions and font
width, height = 220, 220
font = cv2.FONT_HERSHEY_COMPLEX_SMALL

attendance_data = []
marked_students = set(df_existing["Student Name"].unique())  # Prevent duplicate attendance

detection_done = False  # Flag to stop camera after detection

recognition_delay = 30  # frames to hold after detection
hold_frames = 0
while True:
    connected, image = camera.read()
    if not connected:
        break
    
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detections = face_detector.detectMultiScale(
        image_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
        )

    for (x, y, w, h) in detections:
        image_face = cv2.resize(image_gray[y:y + w, x:x + h], (width, height))
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

        id, confidence = face_recognizer.predict(image_face)
        name = user_dict.get(id, "Unknown")  # Get name from CSV
        email = email_dict.get(id, "")


        cv2.putText(image, f"Name: {name}", (x, y + h + 30), font, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Confidence: {round(confidence, 2)}", (x, y + h + 60), font, 1, (0, 255, 0), 1)
        
        if confidence > 65 and name != "Unknown" and name not in marked_students:
            attendance_data.append([current_date, current_day, teacher_name, name, "P"])
            marked_students.add(name)
            print(f"Attendance marked for {name} (Confidence: {confidence:.2f})")  
            if email:
                send_email(email, name, teacher_name, current_date)  
            hold_frames = recognition_delay
    if hold_frames > 0:
        hold_frames -= 1
    else:
        if len(attendance_data) > 0:  # Someone was recognized
            break  # Exit loop after the delay
        key = cv2.waitKey(1)
        if key == ord('q'):
            break 
    cv2.imshow("Face Recognition", image)

    if detection_done:  # If detection is complete, break the loop
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Allow manual exit
        break

# Release camera and close window
camera.release()
cv2.destroyAllWindows()

# Append new attendance data to the existing file
df_new = pd.DataFrame(attendance_data, columns=["Date", "Day", "Teacher", "Student Name", "Status"])
df_final = pd.concat([df_existing, df_new], ignore_index=True)
df_final.to_excel(attendance_file, index=False)

print(f"Attendance saved successfully in {attendance_file}")
