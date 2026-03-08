from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "sseas.db"

# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# CREATE TABLES
# -------------------------
@app.route("/init")
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        branch TEXT,
        year INTEGER,
        CGPA REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Skills (
        skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        location TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        min_CGPA REAL,
        company_id INTEGER,
        FOREIGN KEY(company_id) REFERENCES Companies(company_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student_Skills (
        student_id INTEGER,
        skill_id INTEGER,
        PRIMARY KEY (student_id, skill_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Job_Skills (
        job_id INTEGER,
        skill_id INTEGER,
        PRIMARY KEY (job_id, skill_id)
    )
    """)

    conn.commit()
    conn.close()
    return "Database Initialized!"

# -------------------------
# ADD STUDENT
# -------------------------
@app.route("/add_student", methods=["POST"])
def add_student():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Students (name, branch, year, CGPA) VALUES (?, ?, ?, ?)",
        (data["name"], data["branch"], data["year"], data["CGPA"])
    )

    conn.commit()
    conn.close()
    return jsonify({"message": "Student added successfully"})

# -------------------------
# ADD JOB
# -------------------------
@app.route("/add_job", methods=["POST"])
def add_job():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Jobs (job_title, min_CGPA, company_id) VALUES (?, ?, ?)",
        (data["job_title"], data["min_CGPA"], data["company_id"])
    )

    conn.commit()
    conn.close()
    return jsonify({"message": "Job added successfully"})

# -------------------------
# GET ELIGIBLE STUDENTS
# -------------------------
@app.route("/eligible/<int:job_id>")
def eligible_students(job_id):
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT s.*
    FROM Students s
    JOIN Student_Skills ss ON s.student_id = ss.student_id
    JOIN Job_Skills js ON ss.skill_id = js.skill_id
    JOIN Jobs j ON j.job_id = js.job_id
    WHERE j.job_id = ?
    AND s.CGPA >= j.min_CGPA
    """

    cursor.execute(query, (job_id,))
    students = cursor.fetchall()

    result = [dict(row) for row in students]

    conn.close()
    return jsonify(result)

# -------------------------
# ANALYTICS: SKILL DEMAND
# -------------------------
@app.route("/skill_demand")
def skill_demand():
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT sk.skill_name, COUNT(js.job_id) as demand
    FROM Skills sk
    JOIN Job_Skills js ON sk.skill_id = js.skill_id
    GROUP BY sk.skill_name
    ORDER BY demand DESC
    """

    cursor.execute(query)
    data = cursor.fetchall()

    result = [{"skill": row[0], "demand": row[1]} for row in data]

    conn.close()
    return jsonify(result)

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)