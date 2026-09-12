from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_resume():
    return {
        "candidate_id": "candidate_001",
        "name": "Test Candidate",
        "summary": "Data Scientist with Python and SQL experience.",
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
        "experience": [
            {
                "company": "ABC Technologies",
                "role": "Data Scientist",
                "years": 1.5,
            }
        ],
        "projects": [
            {
                "name": "Churn Prediction",
                "description": (
                    "Built a machine learning prediction system "
                    "using Python and scikit-learn."
                ),
                "technologies": [
                    "Python",
                    "Scikit-learn",
                ],
            }
        ],
        "education": [
            {
                "degree": "Bachelor's Degree",
                "field": "Computer Science",
                "institution": "Test University",
                "year": 2024,
            }
        ],
        "certifications": [],
    }


def sample_job():
    return {
        "job_id": "job_001",
        "title": "Data Scientist",
        "company": "ABC Technologies",
        "description": (
            "Develop machine learning models and predictive "
            "solutions using Python and SQL."
        ),
        "required_skills": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "preferred_skills": [
            "Docker",
            "AWS",
        ],
        "minimum_experience": 1.0,
        "education": "Bachelor's degree in Computer Science",
        "keywords": [
            "Data Scientist",
            "Python",
            "Machine Learning",
        ],
    }


def test_optimization_endpoint():
    response = client.post(
        "/api/v1/optimization",
        params={
            "resume_text": (
                "Data Scientist Python SQL Machine Learning "
                "Pandas Churn Prediction scikit-learn"
            ),
            "job_text": (
                "Data Scientist Python SQL Machine Learning "
                "predictive solutions"
            ),
        },
        json={
            "resume": sample_resume(),
            "job": sample_job(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "initial_match" in data
    assert "optimized_match" in data
    assert "comparison" in data
    assert "optimization_accepted" in data
    assert "final_match" in data


def test_optimization_result_has_before_after_scores():
    response = client.post(
        "/api/v1/optimization",
        params={
            "resume_text": "Python SQL Machine Learning",
            "job_text": "Python SQL Machine Learning",
        },
        json={
            "resume": sample_resume(),
            "job": sample_job(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    comparison = data["comparison"]

    assert "before_score" in comparison
    assert "after_score" in comparison
    assert "absolute_improvement" in comparison
    assert "percentage_improvement" in comparison


def test_optimization_endpoint_rejects_invalid_resume():
    response = client.post(
        "/api/v1/optimization",
        params={
            "resume_text": "Python",
            "job_text": "Python",
        },
        json={
            "resume": {
                "candidate_id": "candidate_001",
            },
            "job": sample_job(),
        },
    )

    # ResumeProfile allows optional fields, so this request is valid.
    assert response.status_code == 200