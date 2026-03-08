# seed_students.py - Generate 1000 sample students
import sqlite3
import random

DATABASE = "sseas.db"

# Branch and year options
branches = ["CSE", "IT", "ECE", "EE", "ME", "CE", "MCA", "MBA"]
years = [1, 2, 3, 4]

# First and last names for generating random names
first_names = ["Rahul", "Raj", "Ravi", "Rakesh", "Rohit", "Ankit", "Ankur", "Anil", "Amit", "Ajay", "Abhishek", "Aditya", "Akshay", "Arun", "Ashish", "Priya", "Pooja", "Preeti", "Pallavi", "Pankaj", "Vikram", "Vijay", "Vivek", "Vasu", "Vishal", "Varun", "Sneha", "Sonia", "Sonam", "Suman", "Kiran", "Kishore", "Kamal", "Karthik", "Karan", "Neha", "Nisha", "Nikita", "Nidhi", "Naveen", "Nitin", "Gaurav", "Gopal", "Ganesh", "Harsh", "Hiren", "Himanshu", "Jatin", "Jay", "Jaya", "Deepak", "Dinesh", "Chetan", "Chandra", "Bhavin", "Bharat", "Ayush", "Aryan"]

last_names = ["Sharma", "Patel", "Singh", "Kumar", "Gupta", "Joshi", "Shah", "Mehta", "Trivedi", "Mishra", "Reddy", "Rao", "Naidu", "Iyer", "Menon", "Chowdhury", "Mukherjee", "Banerjee", "Das", "Bose", "Agarwal", "Saxena", "Verma", "Tiwari", "Srivastava", "Dwivedi", "Pandey", "Yadav", "Maurya", "Sinha", "Roy", "Chatterjee", "Ganguly", "Saha", "Bajpai", "Shukla", "Mahajan", "Khanna", "Arora", "Malhotra", "Kapoor", "Kohli", "Anand"]

skills = ["Python", "Java", "C++", "JavaScript", "SQL", "Machine Learning", "Data Science", "Web Development", "Mobile Development", "Cloud Computing", "Docker", "Kubernetes", "AWS", "Azure", "React", "Angular", "Node.js", "PHP"]

cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Indore"]
streets = ["Main St", "Park Ave", "Oak Rd", "Lake View", "Hill Top", "River Side", "Garden Road", "Civil Lines", "MG Road"]

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Students")
    cursor.execute("DROP TABLE IF EXISTS Skills")
    cursor.execute("DROP TABLE IF EXISTS Companies")
    cursor.execute("DROP TABLE IF EXISTS Jobs")
    cursor.execute("DROP TABLE IF EXISTS Student_Skills")
    cursor.execute("DROP TABLE IF EXISTS Job_Skills")
    cursor.execute("""CREATE TABLE Students (student_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, branch TEXT, year INTEGER, CGPA REAL, email TEXT, phone TEXT, address TEXT, date_of_birth TEXT, gender TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Skills (skill_id INTEGER PRIMARY KEY AUTOINCREMENT, skill_name TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Companies (company_id INTEGER PRIMARY KEY AUTOINCREMENT, company_name TEXT, location TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Jobs (job_id INTEGER PRIMARY KEY AUTOINCREMENT, job_title TEXT, min_CGPA REAL, company_id INTEGER, salary REAL, description TEXT, FOREIGN KEY(company_id) REFERENCES Companies(company_id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Student_Skills (student_id INTEGER, skill_id INTEGER, PRIMARY KEY (student_id, skill_id))""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Job_Skills (job_id INTEGER, skill_id INTEGER, PRIMARY KEY (job_id, skill_id))""")
    conn.commit()
    return conn

def seed_skills(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Skills")
    if cursor.fetchone()[0] == 0:
        for skill in skills:
            cursor.execute("INSERT INTO Skills (skill_name) VALUES (?)", (skill,))
        conn.commit()

def seed_companies(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Companies")
    if cursor.fetchone()[0] == 0:
        companies = [("Google", "USA"), ("Microsoft", "USA"), ("Amazon", "USA"), ("Apple", "USA"), ("Meta", "USA"), ("TCS", "India"), ("Infosys", "India"), ("Wipro", "India"), ("HCL", "India"), ("Accenture", "India")]
        for name, loc in companies:
            cursor.execute("INSERT INTO Companies (company_name, location) VALUES (?, ?)", (name, loc))
        conn.commit()

def seed_jobs(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Jobs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT company_id FROM Companies")
        company_ids = [row[0] for row in cursor.fetchall()]
        job_titles = ["Software Engineer", "Full Stack Developer", "Data Scientist", "ML Engineer", "Backend Developer", "Frontend Developer", "DevOps Engineer"]
        for _ in range(30):
            job_title = random.choice(job_titles)
            company_id = random.choice(company_ids)
            min_cgpa = round(random.uniform(6.0, 8.5), 1)
            salary = random.randint(300000, 2000000)
            cursor.execute("INSERT INTO Jobs (job_title, min_CGPA, company_id, salary, description) VALUES (?, ?, ?, ?, ?)", (job_title, min_cgpa, company_id, salary, f"Looking for {job_title}"))
        conn.commit()

def generate_students(count=1000):
    print(f"Generating {count} students...")
    conn = create_tables()
    cursor = conn.cursor()
    seed_skills(conn)
    seed_companies(conn)
    seed_jobs(conn)
    cursor.execute("DELETE FROM Students")
    cursor.execute("DELETE FROM Student_Skills")
    conn.commit()
    cursor.execute("SELECT skill_id FROM Skills")
    skill_ids = [row[0] for row in cursor.fetchall()]
    for i in range(count):
        name = random.choice(first_names) + " " + random.choice(last_names)
        branch = random.choice(branches)
        year = random.choice(years)
        cgpa = round(random.uniform(5.0, 10.0), 2)
        first_name_lower = name.split()[0].lower()
        last_name_lower = name.split()[1].lower()
        email = f"{first_name_lower}.{last_name_lower}{random.randint(1, 999)}@student.edu"
        phone = f"+91{random.randint(7000000000, 9999999999)}"
        address = f"{random.randint(1, 999)}, {random.choice(streets)}, {random.choice(cities)}"
        year_birth = random.randint(1998, 2006)
        dob = f"{year_birth}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        gender = random.choice(["Male", "Female"])
        cursor.execute("INSERT INTO Students (name, branch, year, CGPA, email, phone, address, date_of_birth, gender) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, branch, year, cgpa, email, phone, address, dob, gender))
        student_id = cursor.lastrowid
        selected_skills = random.sample(skill_ids, random.randint(2, 5))
        for skill_id in selected_skills:
            cursor.execute("INSERT INTO Student_Skills (student_id, skill_id) VALUES (?, ?)", (student_id, skill_id))
        if (i + 1) % 100 == 0:
            conn.commit()
            print(f"Generated {i + 1} students...")
    conn.commit()
    conn.close()
    print(f"Successfully generated {count} students!")

if __name__ == "__main__":
    generate_students(1000)

