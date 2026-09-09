from app.schemas.resume import (ResumeProfile,Education,Project,Experience)
from app.schemas.job import JobProfile

from src.matching.skill_matcher import (
    match_skills,
    match_required_and_preferred_skills,
)

from src.matching.experience_matcher import (
    calculate_total_experience,
    calculate_experience_score,
    match_experience,
)

from src.matching.project_matcher import (
    calculate_project_score,
    match_projects,
)

from src.matching.education_matcher import (
    normalize_education,
    education_matches,
    calculate_education_score,
    match_education,
)

from src.matching.scoring_engine import calculate_overall_score

from src.evaluation.ats_analyzer import (
    calculate_keyword_coverage,
    analyze_sections,
    analyze_metrics,
    calculate_ats_score,
    analyze_ats,
)

from src.evaluation.skill_gap_analyzer import (
    analyze_skill_gaps,
)

from src.evaluation.score_comparator import compare_scores

def test_skill_match():

    resume_skills = [
        "Python",
        "SQL",
        "Pandas",
        "Scikit-learn",
    ]

    job_skills = [
        "Python",
        "SQL",
        "Pandas",
        "XGBoost",
        "AWS",
    ]

    result = match_skills(
        resume_skills=resume_skills,
        job_skills=job_skills,
    )

    assert result["score"] == 60.0

    assert set(result["matched"]) == {
        "python",
        "sql",
        "pandas",
    }

    assert set(result["missing"]) == {
        "aws",
        "xgboost",
    }


def test_required_and_preferred_matching():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=[
            "Python",
            "SQL",
            "Pandas",
            "FastAPI",
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Pandas",
            "XGBoost",
        ],
        preferred_skills=[
            "FastAPI",
            "AWS",
        ],
    )

    result = match_required_and_preferred_skills(
        resume=resume,
        job=job,
    )

    assert result["required"]["score"] == 75.0
    assert result["preferred"]["score"] == 50.0

from src.matching.semantic_matcher import calculate_semantic_score


def test_semantic_score():

    resume_text = """
    Data Scientist with experience in Python,
    machine learning, predictive modeling,
    data analysis and model development.
    """

    job_text = """
    We are looking for a Data Scientist experienced
    in Python, machine learning, predictive analytics
    and developing machine learning models.
    """

    score = calculate_semantic_score(
        resume_text=resume_text,
        job_text=job_text,
    )

    assert 0 <= score <= 100

def test_calculate_total_experience():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        experience=[
            {
                "company": "Company A",
                "role": "Data Scientist",
                "years": 1.0,
            },
            {
                "company": "Company B",
                "role": "ML Intern",
                "years": 0.5,
            },
        ],
    )

    assert calculate_total_experience(resume) == 1.5

def test_experience_score():
    assert calculate_experience_score(2.0, 2.0) == 100.0
    assert calculate_experience_score(3.0, 2.0) == 100.0
    assert calculate_experience_score(1.0, 2.0) == 50.0
    assert calculate_experience_score(0.0, 2.0) == 0.0
    assert calculate_experience_score(2.0, 0.0) == 100.0

def test_match_experience():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        experience=[
            {
                "company": "Company A",
                "role": "Data Scientist",
                "years": 1.0,
            }
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        minimum_experience=2.0,
    )

    result = match_experience(resume, job)

    assert result["candidate_experience"] == 1.0
    assert result["required_experience"] == 2.0
    assert result["score"] == 50.0
    assert result["meets_requirement"] is False

def test_project_score():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        projects=[
            {
                "name": "Insurance Cost Prediction",
                "description": "Machine learning project for predictive modeling.",
                "technologies": [
                    "Python",
                    "Pandas",
                    "Scikit-learn",
                    "XGBoost",
                ],
            }
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "Machine Learning",
            "Pandas",
            "Scikit-learn",
            "XGBoost",
        ],
    )

    score = calculate_project_score(resume, job)

    assert score > 0
    assert score <= 100

def test_match_projects():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        projects=[
            {
                "name": "ML Project",
                "description": "Machine learning prediction system.",
                "technologies": [
                    "Python",
                    "Scikit-learn",
                ],
            }
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "Machine Learning",
        ],
    )

    result = match_projects(resume, job)

    assert result["project_count"] == 1
    assert result["score"] > 0
    assert len(result["relevant_projects"]) == 1


def test_normalize_education():

    result = normalize_education("B.Sc Computer Science")

    assert "bachelor" in result
    assert "computer" in result
    assert "science" in result


def test_education_matches():

    result = education_matches(
        "BSc Computer Science",
        "Bachelor's degree in Computer Science, Data Science, Statistics, Mathematics, Engineering, or a related field."
    )

    assert result is True


def test_education_score():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        education=[
            {
                "degree": "BSc",
                "field": "Computer Science",
                "institution": "ABC University",
                "year": 2024,
            }
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        education="Bachelor's degree in Computer Science, Data Science, Statistics, Mathematics, Engineering, or a related field.",
    )

    score = calculate_education_score(resume, job)

    assert score == 100.0


def test_match_education():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        education=[
            {
                "degree": "BSc",
                "field": "Computer Science",
                "institution": "ABC University",
                "year": 2024,
            }
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        education="Bachelor's degree in Computer Science, Data Science, Statistics, Mathematics, Engineering, or a related field.",
    )

    result = match_education(resume, job)

    assert result["score"] == 100.0
    assert result["matched"] is True

def test_calculate_overall_score():

    score = calculate_overall_score(
        required_skill_score=80,
        semantic_score=70,
        experience_score=100,
        project_score=90,
        education_score=100,
        preferred_skill_score=60,
    )

    assert score == 81.5


def create_test_resume():
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with experience in Python and Machine Learning.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
            "Scikit-learn",
        ],
        experience=[
            Experience(
                company="ABC Technologies",
                role="Data Scientist",
                years=1.5,
            )
        ],
        projects=[
            Project(
                name="Insurance Cost Prediction",
                description="Built a machine learning model using Python, Pandas and XGBoost.",
                technologies=[
                    "Python",
                    "Pandas",
                    "XGBoost",
                ],
            )
        ],
        education=[
            Education(
                degree="BSc",
                field="Computer Science",
                institution="ABC University",
                year=2024,
            )
        ],
    )


def create_test_job():
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        company="ABC Technologies",
        description="Data Scientist role requiring Python, SQL and Machine Learning.",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "XGBoost",
            "Docker",
        ],
        minimum_experience=1.0,
        education="Bachelor's degree in Computer Science.",
        keywords=[
            "Data Scientist",
            "Python",
            "SQL",
            "Machine Learning",
            "XGBoost",
        ],
    )


def test_keyword_coverage():

    resume = create_test_resume()
    job = create_test_job()

    resume_text = """
    Data Scientist with experience in Python, SQL,
    Machine Learning, Pandas, Scikit-learn and XGBoost.
    """

    result = calculate_keyword_coverage(
        resume_text,
        job,
    )

def test_section_analysis():

    resume = create_test_resume()

    result = analyze_sections(resume)

    assert result["score"] == 100.0
    assert result["missing_sections"] == []


def test_metrics_analysis():

    resume_text = """
    Improved model performance by 18%.
    Achieved 94% R2.
    Processed 100K records.
    """

    result = analyze_metrics(resume_text)

    assert result["has_metrics"] is True
    assert result["metric_count"] >= 3
    assert result["score"] == 100.0


def test_calculate_ats_score():

    score = calculate_ats_score(
        keyword_score=80,
        section_score=100,
        title_score=100,
        project_score=80,
        metric_score=75,
        formatting_score=100,
    )

    assert score == 86.25


def test_analyze_ats():

    resume = create_test_resume()
    job = create_test_job()

    resume_text = """
    Data Scientist with experience in Python, SQL,
    Machine Learning, Pandas, Scikit-learn and XGBoost.

    Experience:
    Improved model performance by 18%.

    Projects:
    Insurance Cost Prediction using Python, Pandas and XGBoost.

    Education:
    BSc Computer Science.
    """

    result = analyze_ats(
        resume=resume,
        job=job,
        resume_text=resume_text,
    )

    assert 0 <= result["ats_score"] <= 100
    assert "keyword_analysis" in result
    assert "section_analysis" in result
    assert "project_analysis" in result
    assert "recommendations" in result

def test_skill_gap_analysis():

    resume = create_test_resume()
    job = create_test_job()

    result = analyze_skill_gaps(
        resume=resume,
        job=job,
    )

    assert "python" in result["matched_required"]
    assert "sql" in result["matched_required"]
    assert "machine learning" in result["matched_required"]

    assert "docker" in result["missing_preferred"]

    assert result["required_coverage"] == 100.0
    assert result["preferred_coverage"] == 0.0


def test_required_skill_gap_priority():

    resume = ResumeProfile(
        candidate_id="candidate_002",
        skills=["Python"],
    )

    job = JobProfile(
        job_id="job_002",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Statistics",
        ],
        preferred_skills=[
            "Docker",
        ],
    )

    result = analyze_skill_gaps(
        resume=resume,
        job=job,
    )

    assert "sql" in result["missing_required"]
    assert "statistics" in result["missing_required"]

    high_priority_gaps = [
        gap
        for gap in result["gaps"]
        if gap["priority"] == "high"
    ]

    assert len(high_priority_gaps) == 2


def test_preferred_skill_gap_priority():

    resume = ResumeProfile(
        candidate_id="candidate_003",
        skills=[
            "Python",
            "SQL",
        ],
    )

    job = JobProfile(
        job_id="job_003",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
        ],
        preferred_skills=[
            "Docker",
            "MLflow",
        ],
    )

    result = analyze_skill_gaps(
        resume=resume,
        job=job,
    )

    medium_priority_gaps = [
        gap
        for gap in result["gaps"]
        if gap["priority"] == "medium"
    ]

    assert len(medium_priority_gaps) == 2


def test_no_skill_gaps():

    resume = ResumeProfile(
        candidate_id="candidate_004",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Docker",
        ],
    )

    job = JobProfile(
        job_id="job_004",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
        ],
    )

    result = analyze_skill_gaps(
        resume=resume,
        job=job,
    )

    assert result["missing_required"] == []
    assert result["missing_preferred"] == []

    assert len(result["learning_path"]) == 1
    assert result["learning_path"][0]["priority"] == "low"

def test_score_comparison_improvement():
    before = {
        "overall_score": 72.5,
        "breakdown": {
            "required_skill_score": 70.0,
            "semantic_score": 75.0,
            "experience_score": 80.0,
            "project_score": 60.0,
            "education_score": 90.0,
            "preferred_skill_score": 50.0,
        },
    }

    after = {
        "overall_score": 86.0,
        "breakdown": {
            "required_skill_score": 90.0,
            "semantic_score": 85.0,
            "experience_score": 80.0,
            "project_score": 85.0,
            "education_score": 90.0,
            "preferred_skill_score": 70.0,
        },
    }

    result = compare_scores(before, after)

    assert result["before_score"] == 72.5
    assert result["after_score"] == 86.0
    assert result["absolute_improvement"] == 13.5
    assert result["percentage_improvement"] == 18.62
    assert result["improved"] is True

    assert result["component_deltas"]["required_skill_score"] == 20.0
    assert result["component_deltas"]["semantic_score"] == 10.0
    assert result["component_deltas"]["project_score"] == 25.0


def test_score_comparison_no_improvement():
    before = {
        "overall_score": 80.0,
        "breakdown": {
            "required_skill_score": 80.0,
            "semantic_score": 80.0,
        },
    }

    after = {
        "overall_score": 80.0,
        "breakdown": {
            "required_skill_score": 80.0,
            "semantic_score": 80.0,
        },
    }

    result = compare_scores(before, after)

    assert result["before_score"] == 80.0
    assert result["after_score"] == 80.0
    assert result["absolute_improvement"] == 0.0
    assert result["percentage_improvement"] == 0.0
    assert result["improved"] is False


def test_score_comparison_decline():
    before = {
        "overall_score": 90.0,
        "breakdown": {
            "required_skill_score": 90.0,
        },
    }

    after = {
        "overall_score": 85.0,
        "breakdown": {
            "required_skill_score": 80.0,
        },
    }

    result = compare_scores(before, after)

    assert result["absolute_improvement"] == -5.0
    assert result["percentage_improvement"] == -5.56
    assert result["improved"] is False
    assert result["component_deltas"]["required_skill_score"] == -10.0