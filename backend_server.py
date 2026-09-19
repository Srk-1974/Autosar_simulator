from flask import Flask, request, jsonify, send_from_directory
import json
import os

# Serve static files from the current directory
app = Flask(__name__, static_folder='.', static_url_path='')

DB_FILE = 'student_progress.json'

DEFAULT_STATE = {
    "student_id": "STU-001",
    "moduleProgress": [0, 0, 0, 0, 0, 0, 0],
    "labsDone": [0, 0, 0, 0, 0, 0, 0],
    "quizScores": [None, None, None, None, None, None, None],
    "hoursSpent": 0
}

def load_progress():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_STATE

def save_progress(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/progress', methods=['GET'])
def get_progress():
    return jsonify(load_progress())

@app.route('/api/progress', methods=['POST'])
def update_progress():
    data = request.json
    current = load_progress()
    
    if 'moduleProgress' in data: current['moduleProgress'] = data['moduleProgress']
    if 'labsDone' in data: current['labsDone'] = data['labsDone']
    if 'quizScores' in data: current['quizScores'] = data['quizScores']
    if 'hoursSpent' in data: current['hoursSpent'] = data['hoursSpent']
        
    save_progress(current)
    return jsonify({"status": "success", "message": "Progress saved."})

@app.route('/api/reset', methods=['POST'])
def reset_progress():
    save_progress(DEFAULT_STATE)
    return jsonify({"status": "success", "message": "Progress reset."})

@app.route('/')
def serve_portal():
    return send_from_directory('.', 'autosar_portal.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("Starting AUTOSAR Training Server on http://127.0.0.1:5000")
    app.run(debug=False, port=5000, host='0.0.0.0')
