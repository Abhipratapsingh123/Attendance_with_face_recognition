import cv2
import os
import sys
import csv

# Initialize the face detector
face_detector = cv2.CascadeClassifier(
    "C:\\Users\\abhip\\Desktop\\Minor-Project\\models\\haarcascade_frontalface_default.xml")

# Start video capture
camera = cv2.VideoCapture(0)

# Check if person ID and name are provided
if len(sys.argv) != 4:
    print(
        f"Error: Expected 3 arguments (ID, Name, Email), but got {len(sys.argv)-1}.")
    sys.exit(1)


person_id = sys.argv[1]
person_name = sys.argv[2]
person_email = sys.argv[3]

# Define the uploads directory
uploads = "uploads"
if not os.path.exists(uploads):
    os.makedirs(uploads)

# Define the user data file path (store in 'database' folder)
user_data_file = os.path.join("database", "users.csv")      

# Check if the ID already exists
existing_ids = {fname.split(".")[1] for fname in os.listdir(
    uploads) if fname.startswith("user.")}

if person_id in existing_ids:
    print(
        f"Error: ID {person_id} already exists! Please choose a different ID.")
    sys.exit(1)

# Save user data in users.csv


def save_user(person_id, person_name, person_email):
    file_exists = os.path.exists(user_data_file)

    with open(user_data_file, "a", newline="") as file:
        writer = csv.writer(file)

        # Write header if the file is new
        if not file_exists:
            writer.writerow(["ID", "Name", "Email"])

        writer.writerow([person_id, person_name, person_email])


save_user(person_id, person_name, person_email)

image_count = 0

while True:
    ret, frame = camera.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_detector.detectMultiScale(
        gray_frame,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(30, 30)
    )

    for (x, y, w, h) in faces:
        image_count += 1
        face_image = gray_frame[y:y+h, x:x+w]

        # Save the image to the uploads directory
        cv2.imwrite(os.path.join(
            uploads, f"user.{person_id}.{image_count}.jpg"), face_image)

        # Draw a rectangle around the detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Capturing Faces", frame)

    # Stop after capturing 65 images per person
    if image_count >= 65:
        break

    # Press 'q' to stop manually
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

print(
    f"Collected {image_count} images for person ID {person_id}. Data saved in users.csv.")
