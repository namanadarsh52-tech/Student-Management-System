import sqlite3
conn = sqlite3.connect('sseas.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables:", tables)

c.execute("SELECT COUNT(*) FROM Jobs")
jobs = c.fetchone()[0]
print("Jobs:", jobs)

c.execute("SELECT COUNT(*) FROM Companies")
companies = c.fetchone()[0]
print("Companies:", companies)

if jobs == 0:
    print("\nNo jobs found. Need to seed data.")
else:
    print("\nJobs exist!")
    c.execute("SELECT * FROM Jobs LIMIT 3")
    for row in c.fetchall():
        print(row)

conn.close()
