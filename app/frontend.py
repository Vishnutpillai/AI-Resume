from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

import requests
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.ingestion.document_loader import load_document
from src.extraction.resume_extractor import extract_resume
from src.extraction.jd_extractor import extract_job


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Resume Job Matcher",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

SESSION_DEFAULTS = {
    "resume_profile": None,
    "resume_text": "",
    "job_profile": None,
    "job_text": "",
    "analysis_result": None,
    "optimization_result": None,
    "recommendation_result": None,
    "final_resume": None,
    "docx_bytes": None,
}


def initialize_session_state() -> None:
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


initialize_session_state()


# ============================================================
# HELPERS
# ============================================================

def numeric(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """

    if value is None:
        return default

    if isinstance(value, bool):
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def score_text(value: Any) -> str:
    return f"{numeric(value):.2f}%"


def save_uploaded_file(
    uploaded_file,
) -> Path:
    """
    Save Streamlit UploadedFile temporarily.
    """

    suffix = Path(
        uploaded_file.name
    ).suffix.lower()

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    )

    temp_file.write(
        uploaded_file.getvalue()
    )

    temp_file.close()

    return Path(
        temp_file.name
    )


def parse_uploaded_file(
    uploaded_file,
) -> str:
    """
    Parse uploaded file through existing
    document ingestion pipeline.
    """

    temp_path = save_uploaded_file(
        uploaded_file
    )

    try:
        return load_document(
            str(temp_path)
        )

    finally:
        try:
            temp_path.unlink(
                missing_ok=True
            )

        except OSError:
            pass


def extract_job_title(
    text: str,
    default_title: str,
) -> str:

    if not text or not text.strip():
        return default_title

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return default_title

    first_line = lines[0]

    if len(first_line) <= 100:
        return first_line

    return default_title


def split_pasted_jobs(
    text: str,
) -> list[str]:

    if not text or not text.strip():
        return []

    return [
        section.strip()
        for section in text.split(
            "---JOB---"
        )
        if section.strip()
    ]


# ============================================================
# API REQUEST
# ============================================================

def api_request(
    method: str,
    endpoint: str,
    api_url: str,
    **kwargs,
):
    """
    Send HTTP request to FastAPI backend.
    """

    url = (
        f"{api_url.rstrip('/')}"
        f"{endpoint}"
    )

    try:

        response = requests.request(
            method=method,
            url=url,
            timeout=180,
            **kwargs,
        )

    except requests.RequestException as exc:

        st.error(
            "Could not connect to FastAPI backend."
        )

        st.code(
            str(exc)
        )

        return None

    if response.status_code >= 400:

        st.error(
            "API request failed."
        )

        st.write(
            f"HTTP Status: {response.status_code}"
        )

        try:

            st.json(
                response.json()
            )

        except ValueError:

            st.code(
                response.text
            )

        return None

    content_type = (
        response.headers.get(
            "content-type",
            "",
        )
        .lower()
    )

    if "application/json" in content_type:

        try:

            return response.json()

        except ValueError:

            st.error(
                "FastAPI returned invalid JSON."
            )

            return None

    return response


# ============================================================
# ANALYSIS RESPONSE HELPERS
# ============================================================

def get_analysis_container(
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """
    Get deterministic analysis container.
    """

    if not isinstance(
        analysis,
        dict,
    ):
        return {}

    deterministic = analysis.get(
        "deterministic_analysis"
    )

    if isinstance(
        deterministic,
        dict,
    ):
        return deterministic

    return analysis


def get_match_result(
    analysis: dict[str, Any],
) -> dict[str, Any]:

    container = get_analysis_container(
        analysis
    )

    for key in [
        "match_result",
        "matching_result",
        "matching",
        "match",
        "matching_analysis",
        "score_result",
    ]:

        value = container.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):

            return value

    if any(
        key in container
        for key in [
            "overall_score",
            "match_score",
            "breakdown",
            "skill_match",
        ]
    ):

        return container

    return {}


def get_ats_result(
    analysis: dict[str, Any],
) -> dict[str, Any]:

    container = get_analysis_container(
        analysis
    )

    for key in [
        "ats_result",
        "ats_analysis",
        "ats",
    ]:

        value = container.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):

            return value

    if any(
        key in container
        for key in [
            "ats_score",
            "keyword_analysis",
        ]
    ):

        return container

    return {}


def get_skill_gap_result(
    analysis: dict[str, Any],
) -> dict[str, Any]:

    container = get_analysis_container(
        analysis
    )

    for key in [
        "skill_gap",
        "skill_gap_result",
        "skill_gap_analysis",
    ]:

        value = container.get(
            key
        )

        if isinstance(
            value,
            dict,
        ):

            return value

    return {}


def find_nested_value(
    data: Any,
    keys: set[str],
) -> Any:
    """
    Recursively find a value inside nested
    dictionaries/lists.
    """

    if isinstance(
        data,
        dict,
    ):

        for key, value in data.items():

            if key.lower() in keys:
                return value

        for value in data.values():

            result = find_nested_value(
                value,
                keys,
            )

            if result is not None:
                return result

    elif isinstance(
        data,
        list,
    ):

        for item in data:

            result = find_nested_value(
                item,
                keys,
            )

            if result is not None:
                return result

    return None


def extract_overall_score(
    match_result: dict[str, Any],
    analysis: dict[str, Any],
) -> float:

    score_keys = {
        "overall_score",
        "overall_match",
        "match_score",
        "overall_matching_score",
    }

    value = find_nested_value(
        match_result,
        score_keys,
    )

    if value is not None:
        return numeric(value)

    value = find_nested_value(
        analysis,
        score_keys,
    )

    if value is not None:
        return numeric(value)

    return 0.0


def extract_ats_score(
    ats_result: dict[str, Any],
    analysis: dict[str, Any],
) -> float:

    score_keys = {
        "ats_score",
        "ats_match_score",
    }

    value = find_nested_value(
        ats_result,
        score_keys,
    )

    if value is not None:
        return numeric(value)

    value = find_nested_value(
        analysis,
        score_keys,
    )

    if value is not None:
        return numeric(value)

    return 0.0


def extract_breakdown(
    match_result: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:

    breakdown = match_result.get(
        "breakdown"
    )

    if isinstance(
        breakdown,
        dict,
    ):
        return breakdown

    breakdown = analysis.get(
        "breakdown"
    )

    if isinstance(
        breakdown,
        dict,
    ):
        return breakdown

    value = find_nested_value(
        analysis,
        {"breakdown"},
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def extract_matched_skills(
    match_result: dict[str, Any],
    analysis: dict[str, Any],
) -> list:

    for source in [
        match_result,
        analysis,
    ]:

        for key in [
            "matched_skills",
            "matched",
            "matched_required_skills",
        ]:

            value = source.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    skill_match = match_result.get(
        "skill_match"
    )

    if isinstance(
        skill_match,
        dict,
    ):

        matched = skill_match.get(
            "matched",
            [],
        )

        if isinstance(
            matched,
            list,
        ):
            return matched

    return []


def extract_missing_skills(
    match_result: dict[str, Any],
    analysis: dict[str, Any],
) -> list:

    for source in [
        match_result,
        analysis,
    ]:

        for key in [
            "missing_skills",
            "missing",
            "missing_required_skills",
        ]:

            value = source.get(
                key
            )

            if isinstance(
                value,
                list,
            ):
                return value

    skill_match = match_result.get(
        "skill_match"
    )

    if isinstance(
        skill_match,
        dict,
    ):

        missing = skill_match.get(
            "missing",
            [],
        )

        if isinstance(
            missing,
            list,
        ):
            return missing

    return []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title(
        "Configuration"
    )

    api_url = st.text_input(
        "API URL",
        value=DEFAULT_API_URL,
    )

    st.caption(
        "FastAPI backend used for analysis, "
        "optimization, export, and job recommendations."
    )

    st.divider()

    st.subheader(
        "System"
    )

    st.write(
        "**Resume:**"
    )

    if st.session_state[
        "resume_profile"
    ] is not None:

        st.success(
            "Resume loaded"
        )

    else:

        st.info(
            "No resume loaded"
        )

    st.write(
        "**Job Description:**"
    )

    if st.session_state[
        "job_profile"
    ] is not None:

        st.success(
            "Job description loaded"
        )

    else:

        st.info(
            "No job description loaded"
        )


# ============================================================
# MAIN HEADER
# ============================================================

st.title(
    "Intelligent Resume & Job Matching System"
)

st.write(
    "AI-powered resume analysis, ATS scoring, "
    "job matching, resume optimization, "
    "and job recommendations."
)


# ============================================================
# RESUME INPUT
# ============================================================

st.header(
    "Resume Analysis"
)

st.write(
    "Upload your resume or paste the resume text."
)

resume_file = st.file_uploader(
    "Upload Resume",
    type=[
        "pdf",
        "docx",
        "json",
        "jpg",
        "jpeg",
        "png",
    ],
    key="resume_file",
)

resume_paste = st.text_area(
    "Or Paste Resume Text",
    height=250,
    placeholder=(
        "Paste your complete resume text here..."
    ),
    key="resume_paste",
)


# ============================================================
# JOB INPUT
# ============================================================

st.header(
    "Job Description"
)

st.write(
    "Upload the job description or paste it directly."
)

job_file = st.file_uploader(
    "Upload Job Description",
    type=[
        "pdf",
        "docx",
        "json",
        "txt",
    ],
    key="job_file",
)

job_paste = st.text_area(
    "Or Paste Job Description",
    height=250,
    placeholder=(
        "Paste the complete job description here..."
    ),
    key="job_paste",
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "Analyze Resume & Job",
    use_container_width=True,
):

    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    resume_text = ""

    try:

        if resume_file is not None:

            resume_text = parse_uploaded_file(
                resume_file
            )

        elif resume_paste.strip():

            resume_text = (
                resume_paste.strip()
            )

        else:

            st.warning(
                "Please upload a resume "
                "or paste resume text."
            )

            st.stop()

    except Exception as exc:

        st.error(
            "Failed to process resume."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # --------------------------------------------------------
    # JOB
    # --------------------------------------------------------

    job_text = ""

    try:

        if job_file is not None:

            job_text = parse_uploaded_file(
                job_file
            )

        elif job_paste.strip():

            job_text = (
                job_paste.strip()
            )

        else:

            st.warning(
                "Please upload a job description "
                "or paste job text."
            )

            st.stop()

    except Exception as exc:

        st.error(
            "Failed to process job description."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # --------------------------------------------------------
    # PROFILE EXTRACTION
    # --------------------------------------------------------

    resume_profile = extract_resume(
        text=resume_text,
        candidate_id="candidate_ui",
    )

    job_title = extract_job_title(
        text=job_text,
        default_title="Job Description",
    )

    job_profile = extract_job(
        text=job_text,
        job_id="job_ui",
        title=job_title,
    )

    # --------------------------------------------------------
    # SAVE CURRENT INPUT
    # --------------------------------------------------------

    st.session_state[
        "resume_profile"
    ] = resume_profile.model_dump()

    st.session_state[
        "resume_text"
    ] = resume_text

    st.session_state[
        "job_profile"
    ] = job_profile.model_dump()

    st.session_state[
        "job_text"
    ] = job_text

    # --------------------------------------------------------
    # CLEAR OLD RESULTS
    # --------------------------------------------------------

    st.session_state[
        "analysis_result"
    ] = None

    st.session_state[
        "optimization_result"
    ] = None

    st.session_state[
        "recommendation_result"
    ] = None

    st.session_state[
        "final_resume"
    ] = None

    st.session_state[
        "docx_bytes"
    ] = None

    # --------------------------------------------------------
    # ANALYSIS REQUEST
    # --------------------------------------------------------

    analysis_payload = {

        "resume": (
            resume_profile.model_dump()
        ),

        "job": (
            job_profile.model_dump()
        ),

        "resume_text": resume_text,

        "job_text": job_text,

        "use_llm": False,
    }

    with st.spinner(
        "Analyzing resume and job description..."
    ):

        analysis_result = api_request(
            method="POST",
            endpoint="/api/v1/analysis",
            api_url=api_url,
            json=analysis_payload,
        )

    if isinstance(
        analysis_result,
        dict,
    ):

        st.session_state[
            "analysis_result"
        ] = analysis_result

        st.success(
            "Resume and job description analyzed successfully."
        )

    else:

        st.error(
            "Analysis did not return a valid response."
        )


# ============================================================
# INITIAL ANALYSIS
# ============================================================

if (
    st.session_state[
        "resume_profile"
    ] is not None
    and st.session_state[
        "job_profile"
    ] is not None
    and isinstance(
        st.session_state[
            "analysis_result"
        ],
        dict,
    )
):

    analysis_result = (
        st.session_state[
            "analysis_result"
        ]
    )

    st.divider()

    st.header(
        "Initial Analysis"
    )

    # --------------------------------------------------------
    # RESPONSE NORMALIZATION
    # --------------------------------------------------------

    match_result = get_match_result(
        analysis_result
    )

    ats_result = get_ats_result(
        analysis_result
    )

    skill_gap_result = (
        get_skill_gap_result(
            analysis_result
        )
    )

    overall_score = (
        extract_overall_score(
            match_result,
            analysis_result,
        )
    )

    ats_score = (
        extract_ats_score(
            ats_result,
            analysis_result,
        )
    )

    breakdown = extract_breakdown(
        match_result,
        analysis_result,
    )

    matched_skills = (
        extract_matched_skills(
            match_result,
            analysis_result,
        )
    )

    missing_skills = (
        extract_missing_skills(
            match_result,
            analysis_result,
        )
    )

    # --------------------------------------------------------
    # TOP SCORES
    # --------------------------------------------------------

    col1, col2, col3 = (
        st.columns(3)
    )

    with col1:

        st.metric(
            "Overall Match",
            score_text(
                overall_score
            ),
        )

    with col2:

        st.metric(
            "ATS Score",
            score_text(
                ats_score
            ),
        )

    with col3:

        st.metric(
            "Matched Skills",
            len(
                matched_skills
            ),
        )

    # --------------------------------------------------------
    # SCORE BREAKDOWN
    # --------------------------------------------------------

    st.subheader(
        "Score Breakdown"
    )

    breakdown_items = [

        (
            "Required Skills",
            "required_skill_score",
        ),

        (
            "Semantic Similarity",
            "semantic_score",
        ),

        (
            "Experience",
            "experience_score",
        ),

        (
            "Projects",
            "project_score",
        ),

        (
            "Education",
            "education_score",
        ),

        (
            "Preferred Skills",
            "preferred_skill_score",
        ),
    ]

    alternative_keys = {

        "required_skill_score": [
            "required_skills",
            "required_score",
        ],

        "semantic_score": [
            "semantic",
            "semantic_similarity",
        ],

        "experience_score": [
            "experience",
        ],

        "project_score": [
            "project",
            "projects",
        ],

        "education_score": [
            "education",
        ],

        "preferred_skill_score": [
            "preferred_skills",
            "preferred_score",
        ],
    }

    score_cols = st.columns(3)

    for index, (
        label,
        key,
    ) in enumerate(
        breakdown_items
    ):

        value = breakdown.get(
            key
        )

        if value is None:

            for alternative in (
                alternative_keys.get(
                    key,
                    [],
                )
            ):

                if alternative in breakdown:

                    value = (
                        breakdown[
                            alternative
                        ]
                    )

                    break

        with score_cols[
            index % 3
        ]:

            st.metric(
                label,
                score_text(
                    0.0
                    if value is None
                    else value
                ),
            )

    # --------------------------------------------------------
    # SKILL MATCH
    # --------------------------------------------------------

    st.subheader(
        "Skill Match"
    )

    skill_col1, skill_col2 = (
        st.columns(2)
    )

    with skill_col1:

        st.write(
            "**Matched Skills**"
        )

        if matched_skills:

            for skill in matched_skills:

                st.write(
                    f"✅ {skill}"
                )

        else:

            st.info(
                "No matched skills found."
            )

    with skill_col2:

        st.write(
            "**Missing Skills**"
        )

        if missing_skills:

            for skill in missing_skills:

                st.write(
                    f"❌ {skill}"
                )

        else:

            st.success(
                "No missing skills identified."
            )

    # --------------------------------------------------------
    # ATS ANALYSIS
    # --------------------------------------------------------

    with st.expander(
        "ATS Analysis"
    ):

        keyword_analysis = (
            ats_result.get(
                "keyword_analysis",
                {},
            )
            or {}
        )

        if keyword_analysis:

            st.metric(
                "Keyword Coverage",
                score_text(
                    keyword_analysis.get(
                        "overall_coverage",
                        0,
                    )
                ),
            )

            st.write(
                "**Matched Keywords**"
            )

            st.write(
                keyword_analysis.get(
                    "matched_keywords",
                    [],
                )
            )

            st.write(
                "**Missing Keywords**"
            )

            st.write(
                keyword_analysis.get(
                    "missing_keywords",
                    [],
                )
            )

        ats_recommendations = (
            ats_result.get(
                "recommendations",
                [],
            )
            or []
        )

        if ats_recommendations:

            st.write(
                "### ATS Recommendations"
            )

            for recommendation in (
                ats_recommendations
            ):

                st.write(
                    f"• {recommendation}"
                )

    # --------------------------------------------------------
    # SKILL GAP
    # --------------------------------------------------------

    with st.expander(
        "Skill Gap Analysis"
    ):

        if skill_gap_result:

            st.json(
                skill_gap_result
            )

        else:

            st.info(
                "No skill gap information returned."
            )

    # --------------------------------------------------------
    # RAW DEBUG RESPONSE
    # --------------------------------------------------------

    if (
        overall_score == 0
        and ats_score == 0
        and not breakdown
    ):

        with st.expander(
            "Debug: Analysis API Response"
        ):

            st.json(
                analysis_result
            )

    # --------------------------------------------------------
    # GENERAL RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = (
        analysis_result.get(
            "recommendations",
            [],
        )
        or []
    )

    if recommendations:

        st.subheader(
            "Recommendations"
        )

        for recommendation in (
            recommendations
        ):

            st.write(
                f"• {recommendation}"
            )


# ============================================================
# RESUME OPTIMIZATION
# ============================================================

if (
    st.session_state[
        "resume_profile"
    ] is not None
    and st.session_state[
        "job_profile"
    ] is not None
):

    st.divider()

    st.header(
        "Resume Optimization"
    )

    st.write(
        "Optimize the resume using the "
        "evidence-grounded optimization pipeline."
    )

    if st.button(
        "Optimize Resume",
        use_container_width=True,
        key="optimize_resume_button",
    ):

        optimization_payload = {

            "resume": (
                st.session_state[
                    "resume_profile"
                ]
            ),

            "job": (
                st.session_state[
                    "job_profile"
                ]
            ),
        }

        with st.spinner(
            "Optimizing resume..."
        ):

            optimization_response = (
                api_request(
                    method="POST",
                    endpoint="/api/v1/optimization",
                    api_url=api_url,
                    params={
                        "resume_text": (
                            st.session_state[
                                "resume_text"
                            ]
                        ),

                        "job_text": (
                            st.session_state[
                                "job_text"
                            ]
                        ),
                    },
                    json=optimization_payload,
                )
            )

        if isinstance(
            optimization_response,
            dict,
        ):

            st.session_state[
                "optimization_result"
            ] = optimization_response

            st.session_state[
                "docx_bytes"
            ] = None

            st.success(
                "Resume optimization completed."
            )

    # ========================================================
    # DISPLAY OPTIMIZATION RESULT
    # ========================================================

    optimization_result = (
        st.session_state[
            "optimization_result"
        ]
    )

    if isinstance(
        optimization_result,
        dict,
    ):

        # ----------------------------------------------------
        # IMPORTANT:
        # Actual backend structure:
        #
        # initial_match["overall_score"]
        # optimized_match["overall_score"]
        # final_match["overall_score"]
        # ----------------------------------------------------

        initial_match = (
            optimization_result.get(
                "initial_match",
                {},
            )
            or {}
        )

        optimized_match = (
            optimization_result.get(
                "optimized_match",
                {},
            )
            or {}
        )

        final_match = (
            optimization_result.get(
                "final_match",
                {},
            )
            or {}
        )

        # ----------------------------------------------------
        # BEFORE SCORE
        # ----------------------------------------------------

        before_score = numeric(
            initial_match.get(
                "overall_score",
                0,
            )
        )

        # ----------------------------------------------------
        # GENERATED AFTER SCORE
        # ----------------------------------------------------

        generated_after_score = numeric(
            optimized_match.get(
                "overall_score",
                0,
            )
        )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        final_score = numeric(
            final_match.get(
                "overall_score",
                generated_after_score,
            )
        )

        # ----------------------------------------------------
        # IMPROVEMENT
        # ----------------------------------------------------

        improvement = (
            generated_after_score
            - before_score
        )

        # ----------------------------------------------------
        # ACCEPTANCE
        # ----------------------------------------------------

        accepted = bool(
            optimization_result.get(
                "optimization_accepted",
                False,
            )
        )

        # ----------------------------------------------------
        # SCORE CARDS
        # ----------------------------------------------------

        st.subheader(
            "Optimization Score"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:

            st.metric(
                "Before",
                score_text(
                    before_score
                ),
            )

        with col2:

            st.metric(
                "Generated After",
                score_text(
                    generated_after_score
                ),
            )

        with col3:

            st.metric(
                "Improvement",
                f"{improvement:+.2f}%",
            )

        with col4:

            st.metric(
                "Final Score",
                score_text(
                    final_score
                ),
            )

        # ----------------------------------------------------
        # ACCEPTANCE STATUS
        # ----------------------------------------------------

        if accepted:

            st.success(
                "Optimization accepted — "
                "the generated resume did not reduce "
                "the overall match score."
            )

        else:

            st.warning(
                "Optimization rejected — "
                "the generated resume reduced the overall "
                "match score. The original resume is retained."
            )

        # ----------------------------------------------------
        # SCORE COMPARISON
        # ----------------------------------------------------

        comparison = (
            optimization_result.get(
                "comparison",
                {},
            )
            or {}
        )

        if comparison:

            with st.expander(
                "Score Comparison Details"
            ):

                st.json(
                    comparison
                )

        # ----------------------------------------------------
        # INITIAL MATCH DETAILS
        # ----------------------------------------------------

        with st.expander(
            "Initial Match Details"
        ):

            st.json(
                initial_match
            )

        # ----------------------------------------------------
        # GENERATED OPTIMIZED MATCH
        # ----------------------------------------------------

        with st.expander(
            "Generated Optimized Match Details"
        ):

            st.json(
                optimized_match
            )

        # ----------------------------------------------------
        # COMPONENT DELTAS
        # ----------------------------------------------------

        component_deltas = {}

        if isinstance(
            comparison,
            dict,
        ):

            component_deltas = (
                comparison.get(
                    "component_deltas",
                    comparison.get(
                        "breakdown_deltas",
                        {},
                    ),
                )
                or {}
            )

        if component_deltas:

            st.subheader(
                "Component Score Changes"
            )

            delta_cols = st.columns(3)

            for index, (
                component,
                delta,
            ) in enumerate(
                component_deltas.items()
            ):

                with delta_cols[
                    index % 3
                ]:

                    st.metric(
                        component.replace(
                            "_",
                            " ",
                        ).title(),
                        f"{numeric(delta):+.2f}",
                    )

        # ----------------------------------------------------
        # SUGGESTIONS
        # ----------------------------------------------------

        optimization_data = (
            optimization_result.get(
                "optimization",
                {},
            )
            or {}
        )

        suggestions = (
            optimization_data.get(
                "suggestions",
                [],
            )
            or []
        )

        if suggestions:

            st.subheader(
                "Optimization Suggestions"
            )

            for suggestion in (
                suggestions
            ):

                st.write(
                    f"• {suggestion}"
                )

        # ----------------------------------------------------
        # FINAL RESUME
        # ----------------------------------------------------

        final_resume = (
            optimization_result.get(
                "final_resume"
            )
        )

        if not final_resume:

            if accepted:

                final_resume = (
                    optimization_result.get(
                        "optimized_resume"
                    )
                )

            else:

                final_resume = (
                    st.session_state[
                        "resume_profile"
                    ]
                )

        if final_resume:

            st.session_state[
                "final_resume"
            ] = final_resume

            if accepted:

                st.subheader(
                    "Optimized Resume"
                )

            else:

                st.subheader(
                    "Final Resume"
                )

                st.info(
                    "The generated optimization was "
                    "rejected because it did not improve "
                    "the overall match score. The original "
                    "resume is retained."
                )

            with st.expander(
                "View Final Resume"
            ):

                st.json(
                    final_resume
                )

            # ------------------------------------------------
            # DOCX EXPORT
            # ------------------------------------------------

            if st.button(
                "Prepare DOCX",
                use_container_width=True,
                key="prepare_docx_button",
            ):

                with st.spinner(
                    "Preparing DOCX..."
                ):

                    export_response = (
                        api_request(
                            method="POST",
                            endpoint="/api/v1/export/docx",
                            api_url=api_url,
                            json=final_resume,
                        )
                    )

                if export_response is not None:

                    st.session_state[
                        "docx_bytes"
                    ] = (
                        export_response.content
                    )

            if st.session_state[
                "docx_bytes"
            ]:

                st.download_button(
                    label=(
                        "Download Optimized Resume"
                        if accepted
                        else
                        "Download Final Resume"
                    ),

                    data=st.session_state[
                        "docx_bytes"
                    ],

                    file_name=(
                        "optimized_resume.docx"
                        if accepted
                        else
                        "final_resume.docx"
                    ),

                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),

                    use_container_width=True,
                )


# ============================================================
# JOB RECOMMENDATIONS
# ============================================================

st.divider()

st.header(
    "Job Recommendations"
)

st.write(
    "Upload multiple job descriptions or paste multiple "
    "job descriptions and rank them against the current resume."
)


# ============================================================
# UPLOAD MULTIPLE JOB DESCRIPTIONS
# ============================================================

uploaded_jobs = st.file_uploader(
    "Upload Multiple Job Descriptions",
    type=[
        "pdf",
        "docx",
        "json",
        "txt",
    ],
    accept_multiple_files=True,
    key="recommendation_job_files",
)


# ============================================================
# PASTE MULTIPLE JOB DESCRIPTIONS
# ============================================================

st.markdown(
    "**OR paste job descriptions below**"
)

st.caption(
    "For multiple pasted JDs, separate each JD with "
    "`---JOB---`."
)

pasted_jobs = st.text_area(
    "Paste Job Descriptions",
    height=350,
    placeholder=(
        "AI Engineer\n"
        "We are looking for an AI Engineer...\n\n"
        "Required Skills:\n"
        "Python, Machine Learning, FastAPI, Docker\n\n"
        "---JOB---\n\n"
        "Data Scientist\n"
        "We are looking for a Data Scientist...\n\n"
        "Required Skills:\n"
        "Python, SQL, Machine Learning, Pandas"
    ),
    key="recommendation_pasted_jobs",
)


# ============================================================
# RANK JOBS
# ============================================================

if st.button(
    "Rank Jobs",
    use_container_width=True,
    key="rank_jobs_button",
):

    resume_profile = (
        st.session_state.get(
            "resume_profile"
        )
    )

    resume_text = (
        st.session_state.get(
            "resume_text",
            "",
        )
    )

    if resume_profile is None:

        st.warning(
            "Please analyze a resume first."
        )

        st.stop()

    if not resume_text.strip():

        st.warning(
            "Resume text is missing. "
            "Please analyze the resume again."
        )

        st.stop()

    recommendation_jobs = []

    recommendation_job_texts = []

    # ========================================================
    # UPLOADED JOBS
    # ========================================================

    if uploaded_jobs:

        for index, uploaded_file in enumerate(
            uploaded_jobs,
            start=1,
        ):

            try:

                job_text = (
                    parse_uploaded_file(
                        uploaded_file
                    )
                )

                title = Path(
                    uploaded_file.name
                ).stem

                job = extract_job(
                    text=job_text,
                    job_id=(
                        f"uploaded_job_{index}"
                    ),
                    title=title,
                )

                recommendation_jobs.append(
                    job.model_dump()
                )

                recommendation_job_texts.append(
                    job_text
                )

            except Exception as exc:

                st.error(
                    f"Failed to process "
                    f"{uploaded_file.name}"
                )

                st.code(
                    str(exc)
                )

    # ========================================================
    # PASTED JOBS
    # ========================================================

    pasted_sections = (
        split_pasted_jobs(
            pasted_jobs
        )
    )

    starting_number = (
        len(recommendation_jobs)
        + 1
    )

    for offset, job_text in enumerate(
        pasted_sections
    ):

        job_number = (
            starting_number
            + offset
        )

        try:

            title = extract_job_title(
                text=job_text,
                default_title=(
                    f"Pasted Job {job_number}"
                ),
            )

            job = extract_job(
                text=job_text,
                job_id=(
                    f"pasted_job_{job_number}"
                ),
                title=title,
            )

            recommendation_jobs.append(
                job.model_dump()
            )

            recommendation_job_texts.append(
                job_text
            )

        except Exception as exc:

            st.error(
                f"Failed to process "
                f"pasted job {job_number}"
            )

            st.code(
                str(exc)
            )

    # ========================================================
    # VALIDATION
    # ========================================================

    if not recommendation_jobs:

        st.warning(
            "Please upload at least one job description "
            "or paste at least one job description."
        )

        st.stop()

    if len(
        recommendation_jobs
    ) != len(
        recommendation_job_texts
    ):

        st.error(
            "Job profiles and job texts are out of sync."
        )

        st.stop()

    # ========================================================
    # RECOMMENDATION PAYLOAD
    # ========================================================

    recommendation_payload = {

        "resume": resume_profile,

        "resume_text": resume_text,

        "jobs": recommendation_jobs,

        "job_texts": recommendation_job_texts,
    }

    # ========================================================
    # API CALL
    # ========================================================

    with st.spinner(
        f"Ranking {len(recommendation_jobs)} job(s)..."
    ):

        recommendation_result = api_request(
            method="POST",
            endpoint="/api/v1/recommendations",
            api_url=api_url,
            json=recommendation_payload,
        )

    if isinstance(
        recommendation_result,
        dict,
    ):

        st.session_state[
            "recommendation_result"
        ] = recommendation_result

        st.success(
            f"Successfully ranked "
            f"{len(recommendation_jobs)} job(s)."
        )


# ============================================================
# RECOMMENDATION RESULTS
# ============================================================

recommendation_result = (
    st.session_state.get(
        "recommendation_result"
    )
)

if isinstance(
    recommendation_result,
    dict,
):

    st.divider()

    st.header(
        "Recommended Jobs"
    )

    recommendations = (
        recommendation_result.get(
            "recommendations",
            [],
        )
        or []
    )

    total_jobs = (
        recommendation_result.get(
            "total_jobs",
            len(recommendations),
        )
    )

    st.write(
        f"Analyzed **{total_jobs}** "
        "job description(s)."
    )

    if not recommendations:

        st.info(
            "No job recommendations returned."
        )

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        rank = recommendation.get(
            "rank",
            index,
        )

        title = recommendation.get(
            "job_title",
            recommendation.get(
                "title",
                f"Job {index}",
            ),
        )

        company = recommendation.get(
            "company",
            "",
        )

        overall_score = numeric(
            recommendation.get(
                "overall_score",
                recommendation.get(
                    "score",
                    0,
                ),
            )
        )

        heading = (
            f"#{rank} — {title}"
            f" — {overall_score:.2f}%"
        )

        if company:

            heading += (
                f" — {company}"
            )

        with st.expander(
            heading,
            expanded=(rank == 1),
        ):

            st.metric(
                "Overall Match",
                f"{overall_score:.2f}%",
            )

            st.subheader(
                "Score Breakdown"
            )

            breakdown = (
                recommendation.get(
                    "breakdown",
                    {},
                )
                or {}
            )

            recommendation_scores = [

                (
                    "Required Skills",
                    "required_skill_score",
                ),

                (
                    "Semantic Similarity",
                    "semantic_score",
                ),

                (
                    "Experience",
                    "experience_score",
                ),

                (
                    "Projects",
                    "project_score",
                ),

                (
                    "Education",
                    "education_score",
                ),

                (
                    "Preferred Skills",
                    "preferred_skill_score",
                ),
            ]

            cols = st.columns(3)

            for score_index, (
                label,
                key,
            ) in enumerate(
                recommendation_scores
            ):

                value = numeric(
                    breakdown.get(
                        key,
                        recommendation.get(
                            key,
                            0,
                        ),
                    )
                )

                with cols[
                    score_index % 3
                ]:

                    st.metric(
                        label,
                        f"{value:.2f}%",
                    )

            matched = (
                recommendation.get(
                    "matched_skills",
                    recommendation.get(
                        "matched",
                        [],
                    ),
                )
                or []
            )

            missing = (
                recommendation.get(
                    "missing_skills",
                    recommendation.get(
                        "missing",
                        [],
                    ),
                )
                or []
            )

            st.subheader(
                "Skill Match"
            )

            skill_col1, skill_col2 = (
                st.columns(2)
            )

            with skill_col1:

                st.write(
                    "**Matched Skills**"
                )

                if matched:

                    for skill in matched:

                        st.write(
                            f"✅ {skill}"
                        )

                else:

                    st.info(
                        "No matched skills."
                    )

            with skill_col2:

                st.write(
                    "**Missing Skills**"
                )

                if missing:

                    for skill in missing:

                        st.write(
                            f"❌ {skill}"
                        )

                else:

                    st.success(
                        "No missing skills."
                    )

            with st.expander(
                "View Recommendation Details"
            ):

                st.json(
                    recommendation
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Intelligent Resume & Job Matching System "
    "— FastAPI + Streamlit + Semantic Matching + "
    "RAG + Multi-Agent Intelligence"
)