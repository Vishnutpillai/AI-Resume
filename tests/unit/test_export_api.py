from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_docx_export_endpoint():
    resume = {
        "candidate_id": "candidate_001",
        "name": "Test Candidate",
        "summary": "Data Scientist with Python experience.",
        "skills": [
            "Python",
            "SQL",
        ],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }

    response = client.post(
        "/api/v1/export/docx",
        json=resume,
    )

    assert response.status_code == 200

    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    assert len(response.content) > 0


def test_docx_export_rejects_invalid_resume():
    response = client.post(
        "/api/v1/export/docx",
        json={},
    )

    assert response.status_code == 422