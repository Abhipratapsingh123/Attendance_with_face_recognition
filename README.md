# Facial Recognition Based Attendance System

## Project Overview

This project implements an **automated attendance management system** using **facial recognition technology**. It captures student images, trains a machine learning model, recognizes faces in real-time, logs attendance in an Excel file, and sends email notifications to students automatically. The system is designed to replace manual attendance-taking methods and improve reliability and efficiency in educational and institutional environments.
"Designed to run on a local machine" due to hardware access (webcam, email server).

---

## Features

- Real-time face detection using a webcam
- Image capture and storage for training
- Face recognition using the **LBPH algorithm**
- Attendance logging in Excel format
- Automated email notifications via Yagmail
- Modular Python code with structured scripts
- Version-controlled with Git 

---

## Technologies Used

- Python
- OpenCV (Computer Vision)
- LBPH Face Recognizer
- FLASK (for GUI)
- Pandas & NumPy
- Yagmail (for email automation)
- Git & GitHub for version control

## How to use on your system
- First, download the source code to your system by cloning the repository
- Now create a file named ".env" in the main folder and enter your email credentials to implement the email notification service(optional)
- Enter "EMAIL_USER=your email id" and "EMAIL_PASSWORD=app password of your email id in the .env file"
- Adjust the file paths in the code according to your system
- Now open the terminal in the code editor (VS Code) and type the command "python app.py"
- It runs the Flask application in the browser; open the localhost link
- Now on the webpage, enter the unique ID, name, and email address, then press the "Submit User's Info" button
- The camera will open in this step and take 65 photos, storing them in "uploads" folder.
- Also, the user's information gets stored in the "users.csv" file located in the "database" folder
- After this, click on the "Register User" button, which trains an LBPH model on the captured photos and stores the model in the "models" folder
- In the final step, enter the teacher's name and the respective subject, then click on the "Mark Attendance" button. The camera will start again and recognize the face using trained LBPH model, storing the attendance records in the "database" folder
- You can view and download attendance records from the webpage
- You can also view the registered users.
- You can view overall attendance by clicking the "dashboard" button.





