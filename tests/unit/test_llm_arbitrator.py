import pytest

from src.agents.llm_arbitrator import LLMArbitrator


def sample_analysis():
    return {
        "candidate_id": "candidate_001",
        "job_id": "job_001",
        "overall_match_score": 82.5,
        "strengths": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "weaknesses": [
            "AWS",
            "Docker",
        ],
        "skill_gap_analysis": {
            "missing_required_skills": [
                "AWS",
            ],
        },
    }


def test_arbitrator_initialization():
    arbitrator = LLMArbitrator(
        provider="ollama",
        model="qwen3:4b",
    )

    assert arbitrator.provider == "ollama"
    assert arbitrator.model == "qwen3:4b"


def test_build_prompt_contains_analysis():
    arbitrator = LLMArbitrator()

    prompt = arbitrator.build_prompt(
        sample_analysis()
    )

    assert "candidate_001" in prompt
    assert "job_001" in prompt
    assert "82.5" in prompt
    assert "Do not invent" in prompt


def test_build_prompt_contains_grounding_rules():
    arbitrator = LLMArbitrator()

    prompt = arbitrator.build_prompt(
        sample_analysis()
    )

    assert "Do not change the official match score" in prompt
    assert "Never claim that a candidate has a missing skill" in prompt


def test_validate_valid_result():
    result = {
        "summary": "Strong match.",
        "strengths": ["Python", "SQL"],
        "weaknesses": ["AWS"],
        "skill_gaps": ["AWS"],
        "recommendations": [
            "Highlight existing deployment experience."
        ],
    }

    validated = LLMArbitrator._validate_result(result)

    assert validated == result


def test_validate_missing_field():
    result = {
        "summary": "Strong match.",
        "strengths": [],
        "weaknesses": [],
        "skill_gaps": [],
    }

    with pytest.raises(ValueError):
        LLMArbitrator._validate_result(result)


def test_validate_invalid_summary():
    result = {
        "summary": [],
        "strengths": [],
        "weaknesses": [],
        "skill_gaps": [],
        "recommendations": [],
    }

    with pytest.raises(ValueError):
        LLMArbitrator._validate_result(result)


def test_validate_invalid_list_field():
    result = {
        "summary": "Strong match.",
        "strengths": "Python",
        "weaknesses": [],
        "skill_gaps": [],
        "recommendations": [],
    }

    with pytest.raises(ValueError):
        LLMArbitrator._validate_result(result)


def test_arbitrator_rejects_empty_analysis():
    arbitrator = LLMArbitrator()

    with pytest.raises(ValueError):
        arbitrator.arbitrate({})