from __future__ import annotations

from typing import Any

from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile

from src.matching.scoring_engine import calculate_match_result


class JobRecommendationService:
    """
    Rank multiple job descriptions against one resume.

    Uses the existing matching/scoring engine so that job
    recommendations remain consistent with single-job analysis.
    """

    def recommend(
        self,
        resume: ResumeProfile,
        resume_text: str,
        jobs: list[JobProfile],
        job_texts: list[str],
    ) -> list[dict[str, Any]]:
        """
        Rank jobs from highest to lowest match score.
        """

        if resume is None:
            raise ValueError(
                "Resume profile is required."
            )

        if not resume_text or not resume_text.strip():
            raise ValueError(
                "Resume text is required."
            )

        if len(jobs) != len(job_texts):
            raise ValueError(
                "Number of jobs must match number of job texts."
            )

        if not jobs:
            return []

        results: list[dict[str, Any]] = []

        for job, job_text in zip(
            jobs,
            job_texts,
        ):

            if job is None:
                continue

            if not job_text or not job_text.strip():
                continue

            # ------------------------------------------------
            # IMPORTANT
            # Use the same scoring engine as normal analysis.
            # ------------------------------------------------
            match_result = calculate_match_result(
                resume=resume,
                job=job,
                resume_text=resume_text,
                job_text=job_text,
            )

            breakdown = match_result.get(
                "breakdown",
                {},
            )

            skill_match = match_result.get(
                "skill_match",
                {},
            )

            matched_skills = (
                skill_match.get(
                    "matched",
                    [],
                )
                if isinstance(
                    skill_match,
                    dict,
                )
                else []
            )

            missing_skills = (
                skill_match.get(
                    "missing",
                    [],
                )
                if isinstance(
                    skill_match,
                    dict,
                )
                else []
            )

            results.append(
                {
                    "job_id": job.job_id,
                    "job_title": job.title,
                    "title": job.title,
                    "company": job.company,
                    "overall_score": float(
                        match_result.get(
                            "overall_score",
                            0.0,
                        )
                    ),
                    "breakdown": dict(
                        breakdown
                    ),
                    "matched_skills": list(
                        matched_skills
                    ),
                    "missing_skills": list(
                        missing_skills
                    ),
                    "skill_match": (
                        skill_match
                        if isinstance(
                            skill_match,
                            dict,
                        )
                        else {}
                    ),
                    "strengths": list(
                        match_result.get(
                            "strengths",
                            [],
                        )
                        or []
                    ),
                    "weaknesses": list(
                        match_result.get(
                            "weaknesses",
                            [],
                        )
                        or []
                    ),
                    "recommendations": list(
                        match_result.get(
                            "recommendations",
                            [],
                        )
                        or []
                    ),
                }
            )

        # ----------------------------------------------------
        # Highest score first
        # ----------------------------------------------------

        results.sort(
            key=lambda item: float(
                item["overall_score"]
            ),
            reverse=True,
        )

        # ----------------------------------------------------
        # Add ranking
        # ----------------------------------------------------

        for rank, result in enumerate(
            results,
            start=1,
        ):

            result["rank"] = rank

        return results


# ============================================================
# API-FRIENDLY FUNCTION
# ============================================================

def recommend_jobs(
    resume: ResumeProfile,
    resume_text: str,
    jobs: list[JobProfile],
    job_texts: list[str],
) -> dict[str, Any]:
    """
    Return job recommendations in API response format.
    """

    service = JobRecommendationService()

    recommendations = service.recommend(
        resume=resume,
        resume_text=resume_text,
        jobs=jobs,
        job_texts=job_texts,
    )

    return {
        "candidate_id": resume.candidate_id,
        "total_jobs": len(
            recommendations
        ),
        "recommendations": recommendations,
    }


# Backward-compatible alias.
get_job_recommendations = recommend_jobs