from src.ingestion.document_loader import load_document
from src.extraction.resume_extractor import extract_resume
from src.extraction.jd_extractor import extract_job

from src.matching.scoring_engine import calculate_match_result
from src.evaluation.ats_analyzer import analyze_ats
from src.optimization.optimization_pipeline import run_optimization_pipeline


RESUME_PATH = "data/samples/resume.pdf"
JOB_PATH = "data/samples/sample_job.json"


def test_end_to_end_pipeline():

    # 1. Load resume
    resume_text = load_document(RESUME_PATH)

    assert resume_text
    assert len(resume_text) > 100

    # 2. Extract resume
    resume = extract_resume(
        resume_text,
        "candidate_001",
    )

    assert resume.candidate_id == "candidate_001"
    assert resume.name
    assert resume.skills

    # 3. Load job description
    job_text = load_document(JOB_PATH)

    assert job_text

    # 4. Extract job
    job = extract_job(
        job_text,
        "job_001",
        "Data Scientist",
    )

    assert job.job_id == "job_001"
    assert job.title == "Data Scientist"
    assert job.required_skills

    # 5. Matching
    match_result = calculate_match_result(
        resume,
        job,
        resume_text,
        job_text,
    )

    assert "overall_score" in match_result
    assert "breakdown" in match_result

    assert 0 <= match_result["overall_score"] <= 100

    # 6. ATS analysis
    ats_result = analyze_ats(
        resume,
        job,
        resume_text,
    )

    assert "ats_score" in ats_result
    assert 0 <= ats_result["ats_score"] <= 100

    # 7. Optimization
    optimization_result = run_optimization_pipeline(
        resume,
        job,
        resume_text,
        job_text,
    )

    assert optimization_result is not None