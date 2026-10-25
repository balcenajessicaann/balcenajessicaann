
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = "students.db"
CLASSMATE_API_URL = "https://kleinjasperagrabio.onrender.com"
REQUEST_TIMEOUT = 60

PROGRAMS = {"BSIT", "BSED", "BSA", "BSHM", "BSOffAd"}


# ==========================================
# DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def student_to_dict(student):
    return dict(student)


def validate_student_data(data):
    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    program = str(data.get("program", "")).strip()
    section = str(data.get("section", "")).strip()

    try:
        year = int(data.get("year", 0))
    except (TypeError, ValueError):
        return None, "Year level must be a number."

    if not student_id or not name or not program or not section:
        return None, "Please complete all student fields."

    if program not in PROGRAMS:
        return None, "Please select a valid program or department."

    if year not in (1, 2, 3, 4, 5, 6):
        return None, "Year level must be between 1 and 6."

    return {
        "student_id": student_id,
        "name": name,
        "program": program,
        "year": year,
        "section": section,
    }, None


def get_student_by_id(student_id):
    conn = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return student


# ==========================================
# CLASSMATE API INTEGRATION
# ==========================================
def get_classmate_students():
    try:
        response = requests.get(
            f"{CLASSMATE_API_URL}/api/students",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        result = response.json()

        # Accept either a list or a dictionary containing a list.
        if isinstance(result, dict):
            result = result.get("students", result.get("data", []))

        if not isinstance(result, list):
            return {
                "success": False,
                "students": [],
                "message": "The partner API did not return a student list."
            }

        return {
            "success": True,
            "students": result,
            "message": f"Retrieved {len(result)} student record(s) from the partner API."
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "students": [],
            "message": f"Could not connect to the partner API: {error}"
        }
    except ValueError:
        return {
            "success": False,
            "students": [],
            "message": "The partner API returned an invalid JSON response."
        }


# ==========================================
# MAIN DASHBOARD
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# LOCAL STUDENT API - READ AND CREATE
# ==========================================
@app.route("/api/students", methods=["GET", "POST"])
def api_students():
    if request.method == "GET":
        conn = get_db_connection()
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()
        conn.close()

        return jsonify({
            "success": True,
            "students": [student_to_dict(student) for student in students]
        })

    data = request.get_json(silent=True) or {}
    student, error = validate_student_data(data)

    if error:
        return jsonify({"success": False, "message": error}), 400

    source = str(data.get("source", "External API")).strip()
    if not source:
        source = "External API"

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                source
            )
        )
        conn.commit()
        new_id = cursor.lastrowid

        saved_student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (new_id,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "Student added successfully.",
            "student": student_to_dict(saved_student)
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Could not add the student. Check the submitted information."
        }), 400
    finally:
        conn.close()


# ==========================================
# LOCAL STUDENT API - READ, UPDATE, DELETE
# ==========================================
@app.route("/api/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def api_student_detail(student_id):
    existing = get_student_by_id(student_id)

    if not existing:
        return jsonify({
            "success": False,
            "message": "Student record not found."
        }), 404

    if request.method == "GET":
        return jsonify({
            "success": True,
            "student": student_to_dict(existing)
        })

    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        student, error = validate_student_data(data)

        if error:
            return jsonify({"success": False, "message": error}), 400

        conn = get_db_connection()
        conn.execute(
            """
            UPDATE students
            SET student_id = ?, name = ?, program = ?, year = ?, section = ?
            WHERE id = ?
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                student_id
            )
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Student updated successfully.",
            "student": student_to_dict(updated)
        })

    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Student deleted successfully."
    })


# ==========================================
# GET CLASSMATE STUDENTS
# ==========================================
@app.route("/api/classmate-students", methods=["GET"])
def api_classmate_students():
    result = get_classmate_students()
    status = 200 if result["success"] else 502
    return jsonify(result), status


@app.route("/partner-records", methods=["GET"])
def partner_records():
    result = get_classmate_students()
    return jsonify(result), 200 if result["success"] else 502


# ==========================================
# IMPORT CLASSMATE RECORD INTO LOCAL DATABASE
# ==========================================
@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True) or {}
    student, error = validate_student_data(data)

    if error:
        return jsonify({"success": False, "message": error}), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                "Classmate API"
            )
        )
        conn.commit()
        saved = conn.execute(
            "SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "Partner student saved to your database.",
            "student": student_to_dict(saved)
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Could not import this student."
        }), 400
    finally:
        conn.close()


# ==========================================
# SEND STUDENT TO CLASSMATE API
# ==========================================
@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():
    data = request.get_json(silent=True) or {}
    student, error = validate_student_data(data)

    if error:
        return jsonify({"success": False, "message": error}), 400

    partner_data = {
        **student,
        "source": "External API"
    }

    try:
        response = requests.post(
            f"{CLASSMATE_API_URL}/api/students",
            json=partner_data,
            timeout=REQUEST_TIMEOUT
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = {"message": response.text[:500]}

        if response.ok:
            return jsonify({
                "success": True,
                "message": "Student sent successfully to the partner API.",
                "partner_response": partner_response
            })

        return jsonify({
            "success": False,
            "message": f"Partner API returned HTTP {response.status_code}.",
            "partner_response": partner_response
        }), 502

    except requests.RequestException as error:
        return jsonify({
            "success": False,
            "message": f"Could not send the record to the partner API: {error}"
        }), 502


# ==========================================
# OLDER LAB API ROUTES - PRESERVED
# ==========================================
@app.route("/hello", methods=["GET"])
def hello():
    name = request.args.get("name", "Student")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/student", methods=["GET"])
def student_info():
    return jsonify({
        "student_id": "24-00316",
        "name": "Erich Agagdang",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


@app.route("/course", methods=["GET"])
def course_info():
    return jsonify({
        "course_code": "IT",
        "course_name": "Information Technology"
    })


@app.route("/greet", methods=["GET"])
def greet():
    name = request.args.get("name", "Student")
    return jsonify({"greeting": f"Welcome, {name}!"})


@app.route("/profile", methods=["GET"])
def profile():
    return jsonify({
        "name": "Erich Agagdang",
        "program": "BSIT",
        "year": 3
    })


@app.route("/favorite", methods=["GET"])
def favorite():
    return jsonify({
        "favorite_language": "Python",
        "favorite_database": "SQLite"
    })


@app.route("/study", methods=["GET"])
def study():
    return jsonify({
        "message": "Keep practicing Flask APIs and database integration!"
    })


# ==========================================
# OLDER DATABASE ROUTES - PRESERVED
# ==========================================
@app.route("/students", methods=["GET", "POST"])
def students_route():
    if request.method == "GET":
        conn = get_db_connection()
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return jsonify([student_to_dict(student) for student in students])

    data = request.get_json(silent=True) or {}
    student, error = validate_student_data(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student["student_id"], student["name"], student["program"],
            student["year"], student["section"],
            str(data.get("source", "External API"))
        )
    )
    conn.commit()
    saved = conn.execute(
        "SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()

    return jsonify(student_to_dict(saved)), 201


@app.route("/students/<int:student_id>", methods=["GET", "PUT", "DELETE"])
def students_detail_route(student_id):
    if request.method == "GET":
        student = get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student_to_dict(student))

    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        student, error = validate_student_data(data)

        if error:
            return jsonify({"error": error}), 400

        conn = get_db_connection()
        cursor = conn.execute(
            """
            UPDATE students
            SET student_id = ?, name = ?, program = ?, year = ?, section = ?
            WHERE id = ?
            """,
            (
                student["student_id"], student["name"], student["program"],
                student["year"], student["section"], student_id
            )
        )
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


@app.route("/students/section/<section>", methods=["GET"])
def students_by_section(section):
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students WHERE section = ? ORDER BY name",
        (section,)
    ).fetchall()
    conn.close()

    return jsonify([student_to_dict(student) for student in students])


# ==========================================
# RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
