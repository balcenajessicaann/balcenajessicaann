
import sqlite3

DATABASE = "students.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS students")

cursor.execute("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        program TEXT NOT NULL,
        year INTEGER NOT NULL,
        section TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT 'Local'
    )
""")

sample_students = [
    ("24-00316", "Erich Agagdang", "BSIT", 3, "A", "Local"),
    ("24-00111", "JM Abordaje", "BSIT", 3, "B", "Local"),
    ("24-00357", "Mariel Alada", "BSIT", 3, "A", "Local"),
    ("24-00328", "Jaya Mekaela Almodiel", "BSIT", 3, "B", "Local"),
    ("24-00268", "Jessica Ann Balcena", "BSIT", 3, "A", "Local")
]

cursor.executemany("""
    INSERT INTO students
    (student_id, name, program, year, section, source)
    VALUES (?, ?, ?, ?, ?, ?)
""", sample_students)

conn.commit()
conn.close()

print("Database initialized successfully!")
print("The students table and five sample records have been created.")
