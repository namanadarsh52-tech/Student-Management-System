# app.py - Full Featured Flask Student Management System
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "sseas.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database with additional tables
def init_tables():
    conn = get_db()
    cursor = conn.cursor()
    
    # Applications table for hiring
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            job_id INTEGER,
            status TEXT DEFAULT 'pending',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES Students(student_id),
            FOREIGN KEY(job_id) REFERENCES Jobs(job_id)
        )
    """)
    
    # Placements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Placements (
            placement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            company_id INTEGER,
            package REAL,
            join_date DATE,
            FOREIGN KEY(student_id) REFERENCES Students(student_id),
            FOREIGN KEY(company_id) REFERENCES Companies(company_id)
        )
    """)
    
    conn.commit()
    conn.close()

init_tables()

@app.route("/api/init")
def init_db():
    return jsonify({"message": "Database ready with 1000 students!"})

# ============= STUDENTS API =============

@app.route("/api/students", methods=["GET"])
def get_all_students():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)
    offset = (page - 1) * limit
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Students")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM Students ORDER BY student_id LIMIT ? OFFSET ?", (limit, offset))
    students = cursor.fetchall()
    
    conn.close()
    return jsonify({
        "students": [dict(row) for row in students],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    })

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    
    # Get skills
    cursor.execute("""
        SELECT s.skill_name FROM Skills s
        JOIN Student_Skills ss ON s.skill_id = ss.skill_id
        WHERE ss.student_id = ?
    """, (student_id,))
    skills = [row[0] for row in cursor.fetchall()]
    
    # Get applications
    cursor.execute("""
        SELECT a.*, j.job_title, c.company_name 
        FROM Applications a
        JOIN Jobs j ON a.job_id = j.job_id
        JOIN Companies c ON j.company_id = c.company_id
        WHERE a.student_id = ?
    """, (student_id,))
    applications = [dict(row) for row in cursor.fetchall()]
    
    # Get placement
    cursor.execute("""
        SELECT p.*, c.company_name 
        FROM Placements p
        JOIN Companies c ON p.company_id = c.company_id
        WHERE p.student_id = ?
    """, (student_id,))
    placement = cursor.fetchone()
    
    conn.close()
    
    if student:
        data = dict(student)
        data["skills"] = skills
        data["applications"] = applications
        data["placement"] = dict(placement) if placement else None
        return jsonify(data)
    return jsonify({"error": "Student not found"}), 404

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.json
    required = ["name", "branch", "year", "CGPA"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing: {field}"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO Students (name, branch, year, CGPA, email, phone, address, date_of_birth, gender)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"].strip(),
        data["branch"].strip(),
        int(data["year"]),
        float(data["CGPA"]),
        data.get("email", "").strip(),
        data.get("phone", "").strip(),
        data.get("address", "").strip(),
        data.get("date_of_birth", "").strip(),
        data.get("gender", "").strip()
    ))
    
    student_id = cursor.lastrowid
    
    if "skills" in data:
        for skill_name in data["skills"]:
            cursor.execute("SELECT skill_id FROM Skills WHERE skill_name = ?", (skill_name,))
            skill = cursor.fetchone()
            if skill:
                cursor.execute("INSERT INTO Student_Skills VALUES (?, ?)", (student_id, skill[0]))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Student added!", "student_id": student_id}), 201

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    
    cursor.execute("""
        UPDATE Students 
        SET name = ?, branch = ?, year = ?, CGPA = ?, email = ?, phone = ?, address = ?, date_of_birth = ?, gender = ?
        WHERE student_id = ?
    """, (
        data.get("name", "").strip(),
        data.get("branch", "").strip(),
        int(data.get("year", 0)),
        float(data.get("CGPA", 0)),
        data.get("email", "").strip(),
        data.get("phone", "").strip(),
        data.get("address", "").strip(),
        data.get("date_of_birth", "").strip(),
        data.get("gender", "").strip(),
        student_id
    ))
    
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated!"})

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    
    cursor.execute("DELETE FROM Student_Skills WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM Applications WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM Placements WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM Students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Student deleted!"})

@app.route("/api/students/search", methods=["GET"])
def search_students():
    q = request.args.get("q", "")
    branch = request.args.get("branch", "")
    year = request.args.get("year", type=int)
    min_cgpa = request.args.get("min_cgpa", type=float)
    max_cgpa = request.args.get("max_cgpa", type=float)
    gender = request.args.get("gender", "")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 50, type=int)
    offset = (page - 1) * limit
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM Students WHERE 1=1"
    params = []
    
    if q:
        sql += " AND (name LIKE ? OR email LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if branch:
        sql += " AND branch = ?"
        params.append(branch)
    if year:
        sql += " AND year = ?"
        params.append(year)
    if min_cgpa:
        sql += " AND CGPA >= ?"
        params.append(min_cgpa)
    if max_cgpa:
        sql += " AND CGPA <= ?"
        params.append(max_cgpa)
    if gender:
        sql += " AND gender = ?"
        params.append(gender)
    
    count_sql = sql.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]
    
    sql += f" ORDER BY student_id LIMIT {limit} OFFSET {offset}"
    cursor.execute(sql, params)
    students = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        "students": [dict(row) for row in students],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 0
    })

# ============= APPLICATIONS API =============

@app.route("/api/apply", methods=["POST"])
def apply_job():
    data = request.json
    student_id = data.get("student_id")
    job_id = data.get("job_id")
    
    if not student_id or not job_id:
        return jsonify({"error": "student_id and job_id required"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if already applied
    cursor.execute("SELECT * FROM Applications WHERE student_id = ? AND job_id = ?", (student_id, job_id))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Already applied for this job"}), 400
    
    # Check CGPA eligibility
    cursor.execute("SELECT CGPA FROM Students WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    
    cursor.execute("SELECT min_CGPA FROM Jobs WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({"error": "Job not found"}), 404
    
    if student[0] < job[0]:
        conn.close()
        return jsonify({"error": f"CGPA {student[0]} is below minimum required {job[0]}"}), 400
    
    cursor.execute("INSERT INTO Applications (student_id, job_id) VALUES (?, ?)", (student_id, job_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Application submitted!"}), 201

@app.route("/api/applications", methods=["GET"])
def get_all_applications():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, s.name as student_name, s.CGPA, j.job_title, c.company_name
        FROM Applications a
        JOIN Students s ON a.student_id = s.student_id
        JOIN Jobs j ON a.job_id = j.job_id
        JOIN Companies c ON j.company_id = c.company_id
        ORDER BY a.applied_date DESC
    """)
    applications = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in applications])

@app.route("/api/applications/<int:application_id>", methods=["PUT"])
def update_application(application_id):
    data = request.json
    status = data.get("status")
    
    if status not in ["pending", "accepted", "rejected", "interview"]:
        return jsonify({"error": "Invalid status"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Applications SET status = ? WHERE application_id = ?", (status, application_id))
    
    # If accepted, add to placements
    if status == "accepted":
        cursor.execute("SELECT student_id, job_id FROM Applications WHERE application_id = ?", (application_id,))
        app = cursor.fetchone()
        if app:
            cursor.execute("""
                SELECT j.company_id, j.salary FROM Jobs j WHERE j.job_id = ?
            """, (app[1],))
            job = cursor.fetchone()
            if job:
                cursor.execute("""
                    INSERT INTO Placements (student_id, company_id, package, join_date)
                    VALUES (?, ?, ?, date('now'))
                """, (app[0], job[0], job[1]))
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Application updated!"})

# ============= ANALYTICS API =============

@app.route("/api/analytics/stats", methods=["GET"])
def student_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM Students")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(CGPA) FROM Students")
    avg_cgpa = round(cursor.fetchone()[0] or 0, 2)
    
    cursor.execute("SELECT MAX(CGPA) FROM Students")
    max_cgpa = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT MIN(CGPA) FROM Students")
    min_cgpa = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT branch, COUNT(*) as c FROM Students GROUP BY branch ORDER BY c DESC")
    by_branch = [{"branch": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    cursor.execute("SELECT year, COUNT(*) as c FROM Students GROUP BY year ORDER BY year")
    by_year = [{"year": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    cursor.execute("SELECT gender, COUNT(*) as c FROM Students GROUP BY gender")
    by_gender = [{"gender": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) FROM Students WHERE CGPA >= 9")
    cgpa_9_plus = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Students WHERE CGPA >= 7.5 AND CGPA < 9")
    cgpa_7_9 = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Students WHERE CGPA >= 6 AND CGPA < 7.5")
    cgpa_6_75 = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Students WHERE CGPA < 6")
    cgpa_below_6 = cursor.fetchone()[0]
    
    # Placement stats
    cursor.execute("SELECT COUNT(*) FROM Applications")
    total_applications = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Applications WHERE status = 'accepted'")
    placed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Applications WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    # Company stats
    cursor.execute("SELECT COUNT(*) FROM Companies")
    total_companies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Jobs")
    total_jobs = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "total_students": total,
        "average_cgpa": avg_cgpa,
        "max_cgpa": max_cgpa,
        "min_cgpa": min_cgpa,
        "by_branch": by_branch,
        "by_year": by_year,
        "by_gender": by_gender,
        "cgpa_distribution": {
            "9_plus": cgpa_9_plus,
            "7.5_9": cgpa_7_9,
            "6_7.5": cgpa_6_75,
            "below_6": cgpa_below_6
        },
        "placement_stats": {
            "total_applications": total_applications,
            "placed": placed,
            "pending": pending,
            "total_companies": total_companies,
            "total_jobs": total_jobs
        }
    })

# ============= COMPANIES & JOBS API =============

@app.route("/api/skills", methods=["GET"])
def get_all_skills():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Skills ORDER BY skill_name")
    skills = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in skills])

@app.route("/api/companies", methods=["GET"])
def get_companies():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Companies")
    companies = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in companies])

@app.route("/api/companies/<int:company_id>", methods=["GET"])
def get_company(company_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Companies WHERE company_id = ?", (company_id,))
    company = cursor.fetchone()
    
    cursor.execute("SELECT * FROM Jobs WHERE company_id = ?", (company_id,))
    jobs = cursor.fetchall()
    
    cursor.execute("""
        SELECT COUNT(*) FROM Placements WHERE company_id = ?
    """, (company_id,))
    placed = cursor.fetchone()[0]
    
    conn.close()
    
    if company:
        data = dict(company)
        data["jobs"] = [dict(row) for row in jobs]
        data["placed_students"] = placed
        return jsonify(data)
    return jsonify({"error": "Company not found"}), 404

@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, c.company_name, c.location,
        (SELECT COUNT(*) FROM Applications a WHERE a.job_id = j.job_id) as applications
        FROM Jobs j 
        JOIN Companies c ON j.company_id = c.company_id
        ORDER BY j.job_id DESC
    """)
    jobs = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in jobs])

@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.*, c.company_name, c.location 
        FROM Jobs j 
        JOIN Companies c ON j.company_id = c.company_id
        WHERE j.job_id = ?
    """, (job_id,))
    job = cursor.fetchone()
    
    cursor.execute("""
        SELECT COUNT(*) FROM Applications WHERE job_id = ? AND status = 'accepted'
    """, (job_id,))
    selected = cursor.fetchone()[0]
    
    conn.close()
    
    if job:
        data = dict(job)
        data["selected_students"] = selected
        return jsonify(data)
    return jsonify({"error": "Job not found"}), 404

@app.route("/api/jobs/<int:job_id>/eligible", methods=["GET"])
def get_eligible_students(job_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT min_CGPA FROM Jobs WHERE job_id = ?", (job_id,))
    job = cursor.fetchone()
    if not job:
        conn.close()
        return jsonify({"error": "Job not found"}), 404
    
    min_cgpa = job[0]
    
    # Get students who have NOT applied yet
    cursor.execute("""
        SELECT s.* FROM Students s 
        WHERE s.CGPA >= ? 
        AND s.student_id NOT IN (SELECT student_id FROM Applications WHERE job_id = ?)
        ORDER BY s.CGPA DESC
    """, (min_cgpa, job_id))
    students = cursor.fetchall()
    
    # Get already applied
    cursor.execute("""
        SELECT s.*, a.status as application_status FROM Students s
        JOIN Applications a ON s.student_id = a.student_id
        WHERE a.job_id = ?
        ORDER BY s.CGPA DESC
    """, (job_id,))
    applied = cursor.fetchall()
    
    conn.close()
    return jsonify({
        "job_id": job_id,
        "min_cgpa_required": min_cgpa,
        "eligible_students": [dict(row) for row in students],
        "applied_students": [dict(row) for row in applied],
        "eligible_count": len(students),
        "applied_count": len(applied)
    })

# ============= HOME PAGE =============

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Management System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: white; text-align: center; margin-bottom: 30px; font-size: 2.5em; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }
            .stat-card h3 { color: #1e3c72; font-size: 2.5em; margin-bottom: 10px; }
            .stat-card p { color: #666; font-size: 1.1em; }
            .btn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; }
            .btn { display: block; padding: 18px; background: white; color: #1e3c72; text-decoration: none; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.05em; transition: transform 0.2s, box-shadow 0.2s; }
            .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
            .info { background: rgba(255,255,255,0.2); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-top: 30px; }
            .features { background: white; border-radius: 15px; padding: 25px; margin-top: 30px; }
            .features h2 { color: #1e3c72; margin-bottom: 15px; }
            .features ul { list-style: none; padding: 0; }
            .features li { padding: 8px 0; color: #666; border-bottom: 1px solid #eee; }
            .features li:before { content: "✓ "; color: #4CAF50; font-weight: bold; margin-right: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Student Management System</h1>
            <div class="stats-grid">
                <div class="stat-card"><h3>1000</h3><p>Total Students</p></div>
                <div class="stat-card"><h3>10</h3><p>Companies</p></div>
                <div class="stat-card"><h3>30</h3><p>Job Listings</p></div>
                <div class="stat-card"><h3>8</h3><p>Branches</p></div>
            </div>
            <div class="btn-grid">
                <a href="/dashboard.html" class="btn">📊 Dashboard</a>
                <a href="/students.html" class="btn">👥 All Students</a>
                <a href="/search.html" class="btn">🔍 Search</a>
                <a href="/jobs.html" class="btn">💼 Jobs</a>
                <a href="/companies.html" class="btn">🏢 Companies</a>
                <a href="/applications.html" class="btn">📝 Applications</a>
                <a href="/analytics.html" class="btn">📈 Analytics</a>
                <a href="/test_api.html" class="btn">🧪 API Tester</a>
            </div>
            <div class="features">
                <h2>Key Features</h2>
                <ul>
                    <li>Complete Student Database with 1000 students</li>
                    <li>Job Listings with CGPA-based eligibility</li>
                    <li>Online Application System</li>
                    <li>Application Tracking & Status Updates</li>
                    <li>Placement Analytics</li>
                    <li>Company Management</li>
                    <li>Advanced Search & Filtering</li>
                    <li>RESTful API for integration</li>
                </ul>
            </div>
            <div class="info">Server running at http://127.0.0.1:5000</div>
        </div>
    </body>
    </html>
    '''

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        # Check if it's an HTML file
        if filename.endswith('.html'):
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
        return send_from_directory('.', filename)
    except Exception as e:
        return f"File not found: {filename}", 404

if __name__ == "__main__":
    print("="*50)
    print("Student Management System - Enhanced")
    print("Server: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)

