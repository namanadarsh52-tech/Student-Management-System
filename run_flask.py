# run_flask.py - Run this file to start the Flask server
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask
from flask import Flask, request, jsonify, send_from_directory

# Load and execute the Flask app from the other file
exec(open("from flask import Flask, request, jsonif.py").read())

# Serve static HTML files from current directory
@app.route('/')
def index():
    return 'Flask API Running!<br><a href="/test_api.html">Open Test Page</a>'

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('.', filename)
    except:
        return "File not found", 404

if __name__ == "__main__":
    print("="*50)
    print("Flask Student API Server")
    print("Server running at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)

