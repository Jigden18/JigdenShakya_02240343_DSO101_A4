import pytest
from app import app, students, calculate_grade


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_students():
    """Reset in-memory storage before every test so tests don't bleed into each other."""
    students.clear()
    yield
    students.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Helper: quickly add a student via the API ─────────────────────────────────

def add_student(client, name):
    return client.post("/students", json={"name": name})

def add_score(client, name, score):
    return client.post(f"/students/{name}/scores", json={"score": score})


# ═════════════════════════════════════════════════════════════════════════════
# 1. UNIT TESTS — calculate_grade() helper
# ═════════════════════════════════════════════════════════════════════════════

class TestCalculateGrade:

    def test_grade_A_at_90(self):
        assert calculate_grade(90) == "A"

    def test_grade_A_at_100(self):
        assert calculate_grade(100) == "A"

    def test_grade_B_at_85(self):
        assert calculate_grade(85) == "B"

    def test_grade_C_at_75(self):
        assert calculate_grade(75) == "C"

    def test_grade_D_at_65(self):
        assert calculate_grade(65) == "D"

    def test_grade_F_at_50(self):
        assert calculate_grade(50) == "F"

    def test_grade_F_at_zero(self):
        assert calculate_grade(0) == "F"

    def test_boundary_80_is_B_not_C(self):
        assert calculate_grade(80) == "B"

    def test_boundary_79_is_C_not_B(self):
        assert calculate_grade(79) == "C"


# ═════════════════════════════════════════════════════════════════════════════
# 2. HOME ROUTE
# ═════════════════════════════════════════════════════════════════════════════

class TestHomeRoute:

    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_app_name(self, client):
        data = client.get("/").get_json()
        assert data["app"] == "Student Grade Tracker"

    def test_home_lists_endpoints(self, client):
        data = client.get("/").get_json()
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0


# ═════════════════════════════════════════════════════════════════════════════
# 3. ADD STUDENT  — POST /students
# ═════════════════════════════════════════════════════════════════════════════

class TestAddStudent:

    def test_add_student_returns_201(self, client):
        response = add_student(client, "Tenzin")
        assert response.status_code == 201

    def test_add_student_response_contains_name(self, client):
        data = add_student(client, "Tenzin").get_json()
        assert data["name"] == "Tenzin"

    def test_add_student_success_message(self, client):
        data = add_student(client, "Tenzin").get_json()
        assert "added successfully" in data["message"]

    def test_duplicate_student_returns_409(self, client):
        add_student(client, "Tenzin")
        response = add_student(client, "Tenzin")
        assert response.status_code == 409

    def test_missing_name_field_returns_400(self, client):
        response = client.post("/students", json={})
        assert response.status_code == 400

    def test_empty_name_returns_400(self, client):
        response = client.post("/students", json={"name": "   "})
        assert response.status_code == 400

    def test_no_json_body_returns_error(self, client):
        # Flask returns 415 Unsupported Media Type when Content-Type is not JSON
        response = client.post("/students", data="not json",
                               content_type="text/plain")
        assert response.status_code in (400, 415)


# ═════════════════════════════════════════════════════════════════════════════
# 4. LIST STUDENTS — GET /students
# ═════════════════════════════════════════════════════════════════════════════

class TestListStudents:

    def test_empty_list_returns_200(self, client):
        response = client.get("/students")
        assert response.status_code == 200

    def test_empty_list_has_zero_total(self, client):
        data = client.get("/students").get_json()
        assert data["total"] == 0
        assert data["students"] == []

    def test_list_shows_added_students(self, client):
        add_student(client, "Dorji")
        add_student(client, "Pema")
        data = client.get("/students").get_json()
        assert data["total"] == 2
        names = [s["name"] for s in data["students"]]
        assert "Dorji" in names
        assert "Pema" in names

    def test_student_without_scores_shows_NA_grade(self, client):
        add_student(client, "Karma")
        data = client.get("/students").get_json()
        student = data["students"][0]
        assert student["grade"] == "N/A"


# ═════════════════════════════════════════════════════════════════════════════
# 5. GET STUDENT — GET /students/<name>
# ═════════════════════════════════════════════════════════════════════════════

class TestGetStudent:

    def test_get_existing_student_returns_200(self, client):
        add_student(client, "Sonam")
        response = client.get("/students/Sonam")
        assert response.status_code == 200

    def test_get_nonexistent_student_returns_404(self, client):
        response = client.get("/students/Ghost")
        assert response.status_code == 404

    def test_get_student_returns_correct_name(self, client):
        add_student(client, "Sonam")
        data = client.get("/students/Sonam").get_json()
        assert data["name"] == "Sonam"

    def test_get_student_with_no_scores_has_zero_average(self, client):
        add_student(client, "Sonam")
        data = client.get("/students/Sonam").get_json()
        assert data["average"] == 0
        assert data["scores"] == []


# ═════════════════════════════════════════════════════════════════════════════
# 6. ADD SCORE — POST /students/<name>/scores
# ═════════════════════════════════════════════════════════════════════════════

class TestAddScore:

    def test_add_valid_score_returns_201(self, client):
        add_student(client, "Rinchen")
        response = add_score(client, "Rinchen", 85)
        assert response.status_code == 201

    def test_add_score_to_nonexistent_student_returns_404(self, client):
        response = add_score(client, "Nobody", 80)
        assert response.status_code == 404

    def test_score_below_zero_returns_400(self, client):
        add_student(client, "Rinchen")
        response = add_score(client, "Rinchen", -5)
        assert response.status_code == 400

    def test_score_above_100_returns_400(self, client):
        add_student(client, "Rinchen")
        response = add_score(client, "Rinchen", 110)
        assert response.status_code == 400

    def test_non_numeric_score_returns_400(self, client):
        add_student(client, "Rinchen")
        response = client.post("/students/Rinchen/scores", json={"score": "ninety"})
        assert response.status_code == 400

    def test_missing_score_field_returns_400(self, client):
        add_student(client, "Rinchen")
        response = client.post("/students/Rinchen/scores", json={})
        assert response.status_code == 400

    def test_average_calculated_correctly(self, client):
        add_student(client, "Rinchen")
        add_score(client, "Rinchen", 80)
        add_score(client, "Rinchen", 90)
        data = add_score(client, "Rinchen", 70).get_json()
        # (80 + 90 + 70) / 3 = 80.0
        assert data["average"] == 80.0

    def test_grade_returned_after_score_added(self, client):
        add_student(client, "Rinchen")
        data = add_score(client, "Rinchen", 95).get_json()
        assert data["grade"] == "A"

    def test_score_of_zero_is_valid(self, client):
        add_student(client, "Rinchen")
        response = add_score(client, "Rinchen", 0)
        assert response.status_code == 201

    def test_score_of_100_is_valid(self, client):
        add_student(client, "Rinchen")
        response = add_score(client, "Rinchen", 100)
        assert response.status_code == 201


# ═════════════════════════════════════════════════════════════════════════════
# 7. GET GRADE — GET /students/<name>/grade
# ═════════════════════════════════════════════════════════════════════════════

class TestGetGrade:

    def test_grade_for_nonexistent_student_returns_404(self, client):
        response = client.get("/students/Ghost/grade")
        assert response.status_code == 404

    def test_grade_with_no_scores_returns_400(self, client):
        add_student(client, "Lhamo")
        response = client.get("/students/Lhamo/grade")
        assert response.status_code == 400

    def test_grade_A_for_high_scores(self, client):
        add_student(client, "Lhamo")
        add_score(client, "Lhamo", 92)
        add_score(client, "Lhamo", 96)
        data = client.get("/students/Lhamo/grade").get_json()
        assert data["grade"] == "A"

    def test_grade_F_for_low_scores(self, client):
        add_student(client, "Lhamo")
        add_score(client, "Lhamo", 30)
        add_score(client, "Lhamo", 40)
        data = client.get("/students/Lhamo/grade").get_json()
        assert data["grade"] == "F"

    def test_grade_response_contains_average(self, client):
        add_student(client, "Lhamo")
        add_score(client, "Lhamo", 75)
        data = client.get("/students/Lhamo/grade").get_json()
        assert "average" in data
        assert data["average"] == 75.0

    def test_grade_response_contains_name(self, client):
        add_student(client, "Lhamo")
        add_score(client, "Lhamo", 75)
        data = client.get("/students/Lhamo/grade").get_json()
        assert data["name"] == "Lhamo"