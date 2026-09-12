import json
from typing import Any

from app.core.config import settings


ARBITRATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
        },
        "strengths": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "weaknesses": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "skill_gaps": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "summary",
        "strengths",
        "weaknesses",
        "skill_gaps",
        "recommendations",
    ],
    "additionalProperties": False,
}


class LLMArbitrator:
    """
    Use an LLM to synthesize deterministic resume/job analysis
    into a grounded final explanation.

    The LLM does not calculate the official match score and
    must not invent candidate information.
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model

    def build_prompt(
        self,
        analysis: dict[str, Any],
    ) -> str:
        evidence = json.dumps(
            analysis,
            indent=2,
            default=str,
        )

        return f"""
You are an AI resume evaluation assistant.

Analyze ONLY the deterministic evidence provided below.

Rules:
1. Do not invent skills, experience, education, certifications,
   projects, achievements, or metrics.
2. Do not change the official match score.
3. Use only information present in the supplied evidence.
4. Treat the provided strengths, weaknesses, skill gaps, and
   recommendations as evidence.
5. Write a concise professional summary of the evaluation.
6. Never claim that a candidate has a missing skill.
7. Do not copy candidate_id, job_id, overall_match_score, or any
   other input metadata into the response.
8. The response must contain exactly:
   summary
   strengths
   weaknesses
   skill_gaps
   recommendations

DETERMINISTIC ANALYSIS:

{evidence}
""".strip()

    def arbitrate(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        if not analysis:
            raise ValueError("Analysis input is required.")

        if self.provider.lower() != "ollama":
            raise ValueError(
                f"Unsupported LLM provider: {self.provider}"
            )

        prompt = self.build_prompt(analysis)

        try:
            import ollama
        except ImportError as exc:
            raise RuntimeError(
                "Ollama Python package is not installed."
            ) from exc

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                think=False,
                format=ARBITRATION_SCHEMA,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        try:
            content = response["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise ValueError(
                "Ollama response did not contain message content."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise ValueError(
                "Ollama returned empty response content."
            )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM returned invalid JSON."
            ) from exc

        return self._validate_result(result)

    @staticmethod
    def _validate_result(
        result: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ValueError(
                "LLM result must be a JSON object."
            )

        expected_fields = {
            "summary",
            "strengths",
            "weaknesses",
            "skill_gaps",
            "recommendations",
        }

        missing_fields = expected_fields - result.keys()

        if missing_fields:
            raise ValueError(
                f"LLM result is missing fields: {sorted(missing_fields)}"
            )

        unexpected_fields = result.keys() - expected_fields

        if unexpected_fields:
            raise ValueError(
                f"LLM result contains unexpected fields: "
                f"{sorted(unexpected_fields)}"
            )

        if not isinstance(result["summary"], str):
            raise ValueError(
                "LLM summary must be a string."
            )

        for field in (
            "strengths",
            "weaknesses",
            "skill_gaps",
            "recommendations",
        ):
            if not isinstance(result[field], list):
                raise ValueError(
                    f"LLM field '{field}' must be a list."
                )

            if not all(
                isinstance(item, str)
                for item in result[field]
            ):
                raise ValueError(
                    f"All items in '{field}' must be strings."
                )

        return result