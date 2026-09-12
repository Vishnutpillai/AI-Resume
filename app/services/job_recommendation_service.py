from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from src.matching.scoring_engine import calculate_match_result


class JobRecommendationService:
    """
    Rank multiple jobs for a single resume using the existing
    deterministic matching engine.
    """

    def recommend(
        self,
        resume: ResumeProfile,
        resume_text: str,
        jobs: list[JobProfile],
        job_texts: list[str],
    ) -> list[dict[str, object]]:
        if not resume:
            raise ValueError("Resume profile is required.")

        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is required.")

        if not jobs:
            return []

        if len(jobs) != len(job_texts):
            raise ValueError(
                "Number of jobs must match number of job texts."
            )

        results = []

        for job, job_text in zip(jobs, job_texts):
            if not job_text or not job_text.strip():
                continue

            match_result = calculate_match_result(
                resume=resume,
                job=job,
                resume_text=resume_text,
                job_text=job_text,
            )

            results.append(
                {
                    "job_id": job.job_id,
                    "title": job.title,
                    "company": job.company,
                    "overall_score": float(
                        match_result["overall_score"]
                    ),
                    "breakdown": match_result["breakdown"],
                    "skill_match": match_result["skill_match"],
                    "strengths": list(
                        match_result["strengths"]
                    ),
                    "weaknesses": list(
                        match_result["weaknesses"]
                    ),
                    "recommendations": list(
                        match_result["recommendations"]
                    ),
                }
            )

        results.sort(
            key=lambda item: float(
                item["overall_score"]
            ),
            reverse=True,
        )

        for rank, result in enumerate(
            results,
            start=1,
        ):
            result["rank"] = rank

        return results