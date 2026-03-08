import urllib.request
import json

students = [
    {'name': 'Amit', 'branch': 'CSE', 'year': 2, 'CGPA': 9.0},
    {'name': 'Priya', 'branch': 'ECE', 'year': 4, 'CGPA': 8.2},
    {'name': 'Raj', 'branch': 'ME', 'year': 3, 'CGPA': 7.5}
]

for s in students:
    data = json.dumps(s).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:5000/add_student',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    response = urllib.request.urlopen(req).read().decode()
    print(f"Added: {s['name']} - {response}")

