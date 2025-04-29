from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import send_file
import subprocess
import os
import webbrowser
# from subject_summary import generate_summary_chart
from datetime import datetime
import pandas as pd


app = Flask(__name__)

# Define  paths for files
current_date = datetime.now().strftime("%Y-%m-%d")
attendance_file = os.path.join(
    "database", f"attendance_{current_date}.xlsx")
registered_users = os.path.join("database", "users.csv")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/capture', methods=['POST'])
def capture():
    person_id = request.form.get("person_id")
    person_name = request.form.get("person_name")
    person_email = request.form.get("person_email", "default@example.com")
    if not person_id or not person_name or not person_email:
        return jsonify({"error": "Person ID , Name and Email-id are required"}), 400

    # Run capturing script with person_id , person_name and email id
    subprocess.Popen(["python", "capturing_images.py",
                     person_id, person_name, person_email])

    # Redirect to home page after capturing starts
    return redirect(url_for('home'))

# training route


@app.route('/train', methods=['POST'])
def train():
    # Run training script and wait for completion
    subprocess.run(["python", "training.py"], check=True)

    # Redirect to home page after training completes
    return redirect(url_for('home'))


# testing route
@app.route("/start_testing", methods=["POST"])
def start_testing():
    teacher_name = request.form.get("teacher_name")
    subject = request.form.get('subject')

    if not teacher_name and subject:
        return jsonify({"error": "Teacher name and subject is required"}), 400

    try:
        subprocess.run(
            ["python", "testing.py", teacher_name, subject], check=True)
        return render_template("home.html", show_popup=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for opening excel file


@app.route('/open_excel')
def open_excel():
    if os.path.exists(attendance_file):
        webbrowser.open(attendance_file)  # Opens Excel file
    else:
        # Find all attendance files
        attendance_files = [f for f in os.listdir("database") if f.startswith(
            "attendance_") and f.endswith(".xlsx")]

        if attendance_files:
            # Sort files based on modified time, newest first
            attendance_files.sort(key=lambda x: os.path.getmtime(
                os.path.join("database", x)), reverse=True)
            latest_file = os.path.join("database", attendance_files[0])
            # Open the latest available attendance
            webbrowser.open(latest_file)
        else:
            return render_template('home.html', message="No attendance files found.")
    return redirect(url_for('home'))


@app.route('/download_attendance')
def download_attendance():
    if os.path.exists(attendance_file):
        return send_file(attendance_file, as_attachment=True)
    else:
        # Find all attendance files
        attendance_files = [f for f in os.listdir("database") if f.startswith(
            "attendance_") and f.endswith(".xlsx")]

        if attendance_files:
            # Sort by modification time, latest first
            attendance_files.sort(key=lambda x: os.path.getmtime(
                os.path.join("database", x)), reverse=True)
            latest_file = os.path.join("database", attendance_files[0])
            return send_file(latest_file, as_attachment=True)
        else:
            return render_template('home.html', message="No attendance files found.")


@app.route('/registered_users')
def download_registered_users():
    if os.path.exists(registered_users):
        webbrowser.open(registered_users)
    else:
        return render_template('home.html', message="Registered users file not found.")
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    files = [f for f in os.listdir("database") if f.startswith(
        "attendance_") and f.endswith(".xlsx")]
    
    records = []

    for file in files:
        df = pd.read_excel(os.path.join("database", file))
        records.extend(df.to_dict(orient='records'))

    return render_template("dashboard.html", records=records)


if __name__ == "__main__":
    app.run(debug=True)
