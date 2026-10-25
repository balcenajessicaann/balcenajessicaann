
import json
import urllib.request
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# HOME PAGE
# ==========================================
@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
# LAB 4-6: EXISTING API ENDPOINTS
# ==========================================
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


# ==========================================
# LAB 7: DATABASE ENDPOINTS
# ==========================================
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


@app.route('/students/section/<section>')
def get_students_by_section(section):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE section = ?',
        (section,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==========================================
# LAB 8: READ ALL STUDENTS
# GET /api/students
# ==========================================
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students ORDER BY id'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==========================================
# LAB 8: CREATE STUDENT
# POST /api/students
# ==========================================
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON data is required"
        }), 400

    fields = [
        'student_id',
        'name',
        'program',
        'year',
        'section'
    ]

    if any(
        field not in data or
        data[field] is None or
        str(data[field]).strip() == ''
        for field in fields
    ):
        return jsonify({
            "error": "All fields are required"
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                str(data['year']).strip(),
                str(data['section']).strip()
            )
        )

        conn.commit()
        new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "Unable to add student. Check for duplicate IDs."
        }), 400

    conn.close()

    return jsonify({
        "message": "Student added successfully",
        "id": new_id
    }), 201


# ==========================================
# LAB 8: READ ONE STUDENT
# GET /api/students/<id>
# ==========================================
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ==========================================
# LAB 8: UPDATE STUDENT
# PUT /api/students/<id>
# ==========================================
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON data is required"
        }), 400

    fields = [
        'student_id',
        'name',
        'program',
        'year',
        'section'
    ]

    if any(
        field not in data or
        data[field] is None or
        str(data[field]).strip() == ''
        for field in fields
    ):
        return jsonify({
            "error": "All fields are required"
        }), 400

    conn = get_db_connection()

    existing = conn.execute(
        'SELECT id FROM students WHERE id = ?',
        (id,)
    ).fetchone()

    if existing is None:
        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    try:
        conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                str(data['year']).strip(),
                str(data['section']).strip(),
                id
            )
        )

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "Unable to update student. Check for duplicate IDs."
        }), 400

    conn.close()

    return jsonify({
        "message": "Student updated successfully"
    })


# ==========================================
# LAB 8: DELETE STUDENT
# DELETE /api/students/<id>
# ==========================================
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    cursor = conn.execute(
        'DELETE FROM students WHERE id = ?',
        (id,)
    )

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify({
        "message": "Student deleted successfully"
    })


# ==========================================
# LAB 8: RETRIEVE CLASSMATE'S STUDENTS
# GET /api/classmate-students
# ==========================================
@app.route('/api/classmate-students', methods=['GET'])
def get_classmate_students():
    url = "https://abordaje-jm.onrender.com/api/students"

    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            students = json.loads(
                response.read().decode('utf-8')
            )

        if not isinstance(students, list):
            return jsonify({
                "error": "The classmate API did not return a list of students"
            }), 502

        return jsonify(students)

    except Exception as error:
        app.logger.exception(
            "Could not retrieve classmate records"
        )

        return jsonify({
            "error": "Unable to retrieve classmate records",
            "details": str(error)
        }), 502


# ==========================================
# RUN FLASK APPLICATION
# ==========================================
if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
