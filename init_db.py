import sqlite3

DATABASE = "sseas.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Applications table
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
    
    # Create Placements table
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
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:", tables)
    
    # Check Applications
    cursor.execute("SELECT COUNT(*) FROM Applications")
    count = cursor.fetchone()[0]
    print(f"Applications count: {count}")
    
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
