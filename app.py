from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory data store for students and their scores
students = {}


# Helper 

def calculate_grade(average):
    """Return a letter grade for a numeric average (0-100)."""
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"


# Routes 

@app.route("/")
def home():
    return jsonify({
        "app": "Student Grade Tracker",
        "version": "1.1",
        "endpoints": [
            "GET  /students                    - list all students",
            "POST /students                    - add a new student",
            "GET  /students/<name>             - get one student's details",
            "POST /students/<name>/scores      - add a score for a student",
            "GET  /students/<name>/grade       - get final letter grade",
        ]
    })


@app.route("/students", methods=["GET"])
def list_students():
    """Return a summary list of all students."""
    result = []
    for name, data in students.items():
        scores = data["scores"]
        avg = sum(scores) / len(scores) if scores else 0
        result.append({
            "name": name,
            "scores": scores,
            "average": round(avg, 2),
            "grade": calculate_grade(avg) if scores else "N/A",
        })
    return jsonify({"students": result, "total": len(result)}), 200


@app.route("/students", methods=["POST"])
def add_student():
    """Add a new student by name."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Field 'name' is required"}), 400

    name = data["name"].strip()
    if not name:
        return jsonify({"error": "Name cannot be empty"}), 400
    if name in students:
        return jsonify({"error": f"Student '{name}' already exists"}), 409

    students[name] = {"scores": []}
    return jsonify({"message": f"Student '{name}' added successfully", "name": name}), 201


@app.route("/students/<name>", methods=["GET"])
def get_student(name):
    """Return full details for one student."""
    if name not in students:
        return jsonify({"error": f"Student '{name}' not found"}), 404

    scores = students[name]["scores"]
    avg = sum(scores) / len(scores) if scores else 0
    return jsonify({
        "name": name,
        "scores": scores,
        "average": round(avg, 2),
        "grade": calculate_grade(avg) if scores else "N/A",
    }), 200


@app.route("/students/<name>/scores", methods=["POST"])
def add_score(name):
    """Add a numeric score (0-100) for a student."""
    if name not in students:
        return jsonify({"error": f"Student '{name}' not found"}), 404

    data = request.get_json()
    if not data or "score" not in data:
        return jsonify({"error": "Field 'score' is required"}), 400

    score = data["score"]
    if not isinstance(score, (int, float)):
        return jsonify({"error": "Score must be a number"}), 400
    if not (0 <= score <= 100):
        return jsonify({"error": "Score must be between 0 and 100"}), 400

    students[name]["scores"].append(score)
    scores = students[name]["scores"]
    avg = sum(scores) / len(scores)
    return jsonify({
        "message": f"Score {score} added for '{name}'",
        "scores": scores,
        "average": round(avg, 2),
        "grade": calculate_grade(avg),
    }), 201


@app.route("/students/<name>/grade", methods=["GET"])
def get_grade(name):
    """Return the final letter grade for a student."""
    if name not in students:
        return jsonify({"error": f"Student '{name}' not found"}), 404

    scores = students[name]["scores"]
    if not scores:
        return jsonify({"error": f"No scores recorded for '{name}' yet"}), 400

    avg = sum(scores) / len(scores)
    return jsonify({
        "name": name,
        "average": round(avg, 2),
        "grade": calculate_grade(avg),
    }), 200


# Entry point

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)