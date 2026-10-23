import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00268",
        "name": "Jessica Ann Balcena",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })


@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT3120",
        "course_title": "System Integration",
        "instructor": "Dr. Rene Arduo",
        "semester": "First Semester",
        "academic_year": "2026-2027"
    })


@app.route('/greet')
def greet():
    name = request.args.get('name', 'Student')
    section = request.args.get('section', 'BSIT3A')
    return jsonify({
        "message": f"Hello {name} from {section}!"
    })


@app.route('/profile')
def profile():
    return jsonify({
        "student_id": "24-00268",
        "name": "Jessica Ann Balcena",
        "program": "BSIT",
        "year": 3,
        "section": "A",
        "email": "balcenajessicaann@isufst.edu.ph",
        "skills": [
            "Python",
            "HTML",
            "Networking"
        ]
    })


@app.route('/favorite')
def favorite():
    return jsonify({
        "favorite_color": "Pink",
        "favorite_subject": "Math",
        "favorite_artist": "Daniel Caesar",
        "favorite_car": "Jeep Wrangler"
    })


@app.route('/study')
def study():
    subject = request.args.get('subject', 'Programming')
    return jsonify({
        "subject": subject,
        "study_time": "2 hours",
        "activity": "Practice coding",
        "status": "Ready to study"
    })


@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
