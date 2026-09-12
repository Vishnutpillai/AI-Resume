from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_resume_analyze_endpoint():
    payload = {
        "candidate_id": "candidate_001",
        "name": "Test Candidate",
        "summary": "Data Scientist with Python experience.",
        "skills": [
            "Python",
            "SQL",
        ],
        "resume_text": "Data Scientist Python SQL Machine Learning",
    }

    response = client.post(
        "/api/v1/resume/analyze",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == "candidate_001"
    assert data["message"] == "Resume received successfully."
    assert data["text_length"] > 0
    assert data["skills"] == ["Python", "SQL"]


def test_job_analyze_endpoint():
    payload = {
        "job_id": "job_001",
        "title": "Data Scientist",
        "company": "ABC Technologies",
        "description": "Build machine learning solutions.",
        "required_skills": [
            "Python",
            "SQL",
        ],
        "preferred_skills": [
            "Docker",
        ],
        "minimum_experience": 1.0,
        "education": "Bachelor's degree",
        "keywords": [
            "Machine Learning",
        ],
        "job_text": "Data Scientist Python SQL Machine Learning",
    }

    response = client.post(
        "/api/v1/job/analyze",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == "job_001"
    assert data["title"] == "Data Scientist"
    assert data["message"] == "Job description received successfully."
    assert data["text_length"] > 0
    assert data["required_skills"] == ["Python", "SQL"]


def test_resume_analyze_rejects_missing_text():
    payload = {
        "candidate_id": "candidate_001",
        "skills": ["Python"],
    }

    response = client.post(
        "/api/v1/resume/analyze",
        json=payload,
    )

    assert response.status_code == 422