#!/usr/bin/env python
# run_server.py - Initialize database and run Flask server

import sqlite3
import sys

DATABASE = "sseas.db"

def init_database():
    print("Initializing database tables...")
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
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    # Check Applications
    cursor.execute("SELECT COUNT(*) FROM Applications")
    count = cursor.fetchone()[0]
    print(f"Applications: {count}")
    
    conn.close()
    print("Database ready!")

if __name__ == "__main__":
    init_database()
    print("\nStarting Flask server at http://127.0.0.1:5000")
    print("Press Ctrl+C to stop\n")
    
    # Now import and run Flask
    from app import app
    app.run(debug=True, host='127.0.0.1', port=5000)
