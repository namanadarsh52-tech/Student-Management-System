import sqlite3

# Connect to database (creates file if not exists)
conn = sqlite3.connect("sseas.db")
cursor = conn.cursor()

# ----------------------------
# CREATE TABLES
# ----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Students (
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    branch TEXT,
    year INTEGER,
    CGPA REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Skills (
    skill_id INTEGER PRIMARY KEY,
    skill_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT,
    location TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Jobs (
    job_id INTEGER PRIMARY KEY,
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
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY(student_id) REFERENCES Students(student_id),
    FOREIGN KEY(skill_id) REFERENCES Skills(skill_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Job_Skills (
    job_id INTEGER,
    skill_id INTEGER,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY(job_id) REFERENCES Jobs(job_id),
    FOREIGN KEY(skill_id) REFERENCES Skills(skill_id)
)
""")

conn.commit()

# ----------------------------
# INSERT SAMPLE DATA
# ----------------------------

students = [
    (1, "Rahul", "CSE", 3, 8.5),
    (2, "Anita", "IT", 4, 7.8),
    (3, "Vikram", "CSE", 3, 6.9)
]

skills = [
    (101, "Python"),
    (102, "SQL"),
    (103, "Data Analysis")
]

companies = [
    (201, "Infosys", "Bangalore"),
    (202, "TCS", "Hyderabad")
]

jobs = [
    (301, "Data Analyst", 7.5, 201),
    (302, "Software Developer", 7.0, 202)
]

student_skills = [
    (1, 101), (1, 102),
    (2, 101), (2, 103),
    (3, 102)
]

job_skills = [
    (301, 101), (301, 103),
    (302, 101), (302, 102)
]

cursor.executemany("INSERT OR IGNORE INTO Students VALUES (?, ?, ?, ?, ?)", students)
cursor.executemany("INSERT OR IGNORE INTO Skills VALUES (?, ?)", skills)
cursor.executemany("INSERT OR IGNORE INTO Companies VALUES (?, ?, ?)", companies)
cursor.executemany("INSERT OR IGNORE INTO Jobs VALUES (?, ?, ?, ?)", jobs)
cursor.executemany("INSERT OR IGNORE INTO Student_Skills VALUES (?, ?)", student_skills)
cursor.executemany("INSERT OR IGNORE INTO Job_Skills VALUES (?, ?)", job_skills)

conn.commit()

# ----------------------------
# MATCH STUDENTS TO JOB
# ----------------------------

print("\nEligible Students for Data Analyst Job:\n")

query = """
SELECT DISTINCT s.name
FROM Students s
JOIN Student_Skills ss ON s.student_id = ss.student_id
JOIN Job_Skills js ON ss.skill_id = js.skill_id
JOIN Jobs j ON j.job_id = js.job_id
WHERE j.job_id = 301
AND s.CGPA >= j.min_CGPA
"""

cursor.execute(query)

results = cursor.fetchall()

for row in results:
    print(row[0])

# ----------------------------
# ANALYTICS: Top Demanded Skills
# ----------------------------

print("\nMost Demanded Skills:\n")

cursor.execute("""
SELECT sk.skill_name, COUNT(js.job_id) as demand
FROM Skills sk
JOIN Job_Skills js ON sk.skill_id = js.skill_id
GROUP BY sk.skill_name
ORDER BY demand DESC
""")

for row in cursor.fetchall():
    print(f"{row[0]} - Required in {row[1]} jobs")

conn.close()