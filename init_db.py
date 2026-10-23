
import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

cursor.execute("DELETE FROM students")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")

students = [
    ("24-00316", "Erich Agagdang", "BSIT", 3, "A"),
    ("24-00111", "JM Abordaje", "BSIT", 3, "A"),
    ("24-00357", "Mariel Alada", "BSIT", 3, "A"),
    ("24-00328", "Jaya Mekaela Almodiel", "BSIT", 3, "A"),
    ("24-00268", "Jessica Ann Balcena", "BSIT", 3, "A")
]

cursor.executemany("""
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()
conn.close()

print("Database created successfully.")
