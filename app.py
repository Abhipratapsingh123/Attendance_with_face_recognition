from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import send_file
import subprocess
import os
import webbrowser

app = Flask(__name__)

# Define attendance file path
attendance_file = os.path.join("database", "attendance.xlsx")
registered_users = os.path.join("database", "users.csv")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/capture', methods=['POST'])
def capture():
    person_id = request.form.get("person_id")
    person_name = request.form.get("person_name")
    person_email = request.form.get("person_email", "default@example.com")
    if not person_id or not person_name:
        return jsonify({"error": "Person ID and Name are required"}), 400

    # Run capturing script with person_id and person_name
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

    if not teacher_name:
        return jsonify({"error": "Teacher name is required"}), 400

    try:
        subprocess.run(["python", "testing.py", teacher_name], check=True)
        return redirect(url_for('attendance_popup'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/attendance_popup')
def attendance_popup():
    if not os.path.exists(attendance_file):
        return render_template('attendance_popup.html', message="Attendance file not found.")
    return render_template('attendance_popup.html', attendance_file=attendance_file)


@app.route('/open_excel')
def open_excel():
    if os.path.exists(attendance_file):
        webbrowser.open(attendance_file)  # Opens Excel file
    else:
        return render_template('home.html', message="Attendance file not found.")
    return redirect(url_for('home'))


@app.route('/download_attendance')
def download_attendance():
    if os.path.exists(attendance_file):
        return send_file(attendance_file, as_attachment=True)
    return render_template('home.html', message="Attendance file not found.")


@app.route('/registered_users')
def download_registered_users():
    if os.path.exists(registered_users):
        webbrowser.open(registered_users)
    else:
        return render_template('home.html', message="Registered users file not found.")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)  
