import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from src.extraction.jd_extractor import extract_job
from src.extraction.resume_extractor import extract_resume
from src.ingestion.document_loader import load_document


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Intelligent Resume Job Matcher",
    page_icon="📄",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "resume_profile" not in st.session_state:
    st.session_state.resume_profile = None

if "resume_text" not in st.session_state:
    st.session_state.resume_text = None

if "job_profile" not in st.session_state:
    st.session_state.job_profile = None

if "job_text" not in st.session_state:
    st.session_state.job_text = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "optimization_result" not in st.session_state:
    st.session_state.optimization_result = None

if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def save_uploaded_file(uploaded_file) -> str:
    """
    Save a Streamlit UploadedFile to a temporary file.
    """
    suffix = Path(uploaded_file.name).suffix

    with NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(
            uploaded_file.getbuffer()
        )

        return temp_file.name


def extract_resume_from_upload(
    uploaded_file,
) -> tuple[str, dict]:
    """
    Extract raw resume text and ResumeProfile
    from an uploaded resume.
    """
    temp_path = save_uploaded_file(
        uploaded_file
    )

    try:
        text = load_document(temp_path)

        resume_profile = extract_resume(
            text=text,
            candidate_id="streamlit_candidate",
        )

        return (
            text,
            resume_profile.model_dump(),
        )

    finally:
        Path(temp_path).unlink(
            missing_ok=True
        )


def extract_job_from_upload(
    uploaded_file,
) -> tuple[str, dict]:
    """
    Extract raw job description text and JobProfile
    from an uploaded job description.
    """
    temp_path = save_uploaded_file(
        uploaded_file
    )

    try:
        text = load_document(temp_path)

        job_profile = extract_job(
            text=text,
            job_id="streamlit_job",
            title=Path(
                uploaded_file.name
            ).stem,
        )

        return (
            text,
            job_profile.model_dump(),
        )

    finally:
        Path(temp_path).unlink(
            missing_ok=True
        )


def run_analysis(
    api_url: str,
    resume_profile: dict,
    resume_text: str,
    job_profile: dict,
    job_text: str,
) -> dict:
    """
    Call the FastAPI analysis endpoint.
    """
    payload = {
        "resume": resume_profile,
        "job": job_profile,
        "resume_text": resume_text,
        "job_text": job_text,
        "use_llm": False,
    }

    response = requests.post(
        f"{api_url}/api/v1/analysis",
        json=payload,
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


def run_optimization(
    api_url: str,
    resume_profile: dict,
    resume_text: str,
    job_profile: dict,
    job_text: str,
) -> dict:
    """
    Call the FastAPI optimization endpoint.
    """
    response = requests.post(
        f"{api_url}/api/v1/optimization",
        params={
            "resume_text": resume_text,
            "job_text": job_text,
        },
        json={
            "resume": resume_profile,
            "job": job_profile,
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


def export_docx(
    api_url: str,
    resume_profile: dict,
) -> bytes:
    """
    Request optimized DOCX resume from FastAPI.
    """
    response = requests.post(
        f"{api_url}/api/v1/export/docx",
        json=resume_profile,
        timeout=120,
    )

    response.raise_for_status()

    return response.content


def run_job_recommendations(
    api_url: str,
    resume_profile: dict,
    resume_text: str,
    jobs: list[dict],
    job_texts: list[str],
) -> dict:
    """
    Call the FastAPI job recommendation endpoint.
    """
    response = requests.post(
        f"{api_url}/api/v1/recommendations",
        json={
            "resume": resume_profile,
            "resume_text": resume_text,
            "jobs": jobs,
            "job_texts": job_texts,
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "Configuration"
)

api_url = st.sidebar.text_input(
    "API URL",
    value=API_BASE_URL,
)

st.sidebar.caption(
    "FastAPI backend used for analysis, optimization, "
    "export, and job recommendations."
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "Intelligent Resume & Job Matching System"
)

st.write(
    "Upload a resume and job description to analyze the match, "
    "identify skill gaps, optimize the resume, compare results, "
    "and rank multiple jobs."
)


# ============================================================
# RESUME INPUT
# ============================================================

st.header("Resume")

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
    key="resume_upload",
)

resume_text_input = st.text_area(
    "Or paste resume text",
    height=250,
    placeholder="Paste your resume text here...",
)


# ============================================================
# JOB DESCRIPTION INPUT
# ============================================================

st.header("Job Description")

job_file = st.file_uploader(
    "Upload Job Description",
    type=[
        "pdf",
        "docx",
        "json",
        "txt",
    ],
    key="job_upload",
)

job_text_input = st.text_area(
    "Or paste job description",
    height=250,
    placeholder="Paste your job description here...",
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True,
):

    try:

        # ----------------------------------------------------
        # RESUME
        # ----------------------------------------------------

        if resume_file is not None:

            with st.spinner(
                "Extracting resume..."
            ):
                extracted_resume_text, resume_profile = (
                    extract_resume_from_upload(
                        resume_file
                    )
                )

        elif resume_text_input.strip():

            extracted_resume_text = (
                resume_text_input.strip()
            )

            resume_profile = extract_resume(
                text=extracted_resume_text,
                candidate_id="streamlit_candidate",
            ).model_dump()

        else:

            st.error(
                "Please upload a resume or paste resume text."
            )

            st.stop()


        # ----------------------------------------------------
        # JOB DESCRIPTION
        # ----------------------------------------------------

        if job_file is not None:

            with st.spinner(
                "Extracting job description..."
            ):
                extracted_job_text, job_profile = (
                    extract_job_from_upload(
                        job_file
                    )
                )

        elif job_text_input.strip():

            extracted_job_text = (
                job_text_input.strip()
            )

            job_profile = extract_job(
                text=extracted_job_text,
                job_id="streamlit_job",
                title="Target Job",
            ).model_dump()

        else:

            st.error(
                "Please upload a job description or paste job text."
            )

            st.stop()


        # ----------------------------------------------------
        # SAVE TO SESSION
        # ----------------------------------------------------

        st.session_state.resume_profile = (
            resume_profile
        )

        st.session_state.resume_text = (
            extracted_resume_text
        )

        st.session_state.job_profile = (
            job_profile
        )

        st.session_state.job_text = (
            extracted_job_text
        )

        # Reset downstream results
        st.session_state.optimization_result = None
        st.session_state.recommendation_result = None


        # ----------------------------------------------------
        # DISPLAY EXTRACTED INFORMATION
        # ----------------------------------------------------

        with st.expander(
            "View extracted resume information"
        ):
            st.json(
                resume_profile
            )

        with st.expander(
            "View extracted job information"
        ):
            st.json(
                job_profile
            )


        # ----------------------------------------------------
        # ANALYSIS API
        # ----------------------------------------------------

        with st.spinner(
            "Running resume-job analysis..."
        ):

            result = run_analysis(
                api_url=api_url,
                resume_profile=resume_profile,
                resume_text=extracted_resume_text,
                job_profile=job_profile,
                job_text=extracted_job_text,
            )


        st.session_state.analysis_result = (
            result
        )


        st.success(
            "Resume analysis completed successfully."
        )


    except requests.RequestException as exc:

        st.error(
            f"API request failed: {exc}"
        )

        st.stop()

    except Exception as exc:

        st.error(
            f"Analysis failed: {exc}"
        )

        st.stop()


# ============================================================
# INITIAL ANALYSIS RESULTS
# ============================================================

if st.session_state.analysis_result:

    result = st.session_state.analysis_result

    deterministic = result[
        "deterministic_analysis"
    ]

    matching = deterministic[
        "matching_analysis"
    ]

    evaluation = deterministic[
        "evaluation_analysis"
    ]

    skill_analysis = deterministic[
        "skill_analysis"
    ]


    st.divider()

    st.header(
        "Initial Analysis"
    )


    # --------------------------------------------------------
    # SCORE CARDS
    # --------------------------------------------------------

    score = float(
        matching["overall_score"]
    )

    ats_score = None

    ats_analysis = evaluation.get(
        "ats_analysis"
    )

    if isinstance(
        ats_analysis,
        dict,
    ):
        ats_score = ats_analysis.get(
            "ats_score"
        )


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Match Score",
            f"{score:.2f}%",
        )

    with col2:

        if ats_score is not None:

            st.metric(
                "ATS Score",
                f"{float(ats_score):.2f}",
            )

        else:

            st.metric(
                "ATS Score",
                "N/A",
            )

    with col3:

        matched_count = len(
            skill_analysis[
                "matched_required_skills"
            ]
        )

        st.metric(
            "Required Skills Matched",
            matched_count,
        )


    # --------------------------------------------------------
    # MATCH BREAKDOWN
    # --------------------------------------------------------

    st.subheader(
        "Match Breakdown"
    )

    breakdown = matching[
        "breakdown"
    ]

    if isinstance(
        breakdown,
        dict,
    ):

        breakdown_items = list(
            breakdown.items()
        )

        col1, col2 = st.columns(2)

        for index, (
            component,
            component_score,
        ) in enumerate(
            breakdown_items
        ):

            current_column = (
                col1
                if index % 2 == 0
                else col2
            )

            with current_column:

                label = component.replace(
                    "_",
                    " ",
                ).title()

                st.metric(
                    label,
                    f"{float(component_score):.2f}",
                )


    # --------------------------------------------------------
    # SKILL ANALYSIS
    # --------------------------------------------------------

    st.subheader(
        "Skill Analysis"
    )

    skill_col1, skill_col2 = (
        st.columns(2)
    )


    with skill_col1:

        st.write(
            "### Matched Required Skills"
        )

        matched_skills = skill_analysis[
            "matched_required_skills"
        ]

        if matched_skills:

            for skill in matched_skills:

                st.success(
                    skill
                )

        else:

            st.info(
                "No required skills matched."
            )


    with skill_col2:

        st.write(
            "### Missing Required Skills"
        )

        missing_skills = skill_analysis[
            "missing_required_skills"
        ]

        if missing_skills:

            for skill in missing_skills:

                st.error(
                    skill
                )

        else:

            st.success(
                "No required skill gaps detected."
            )


    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.subheader(
        "Recommendations"
    )

    recommendations = matching[
        "recommendations"
    ]

    if recommendations:

        for recommendation in recommendations:

            st.write(
                f"- {recommendation}"
            )

    else:

        st.info(
            "No additional recommendations."
        )


# ============================================================
# RESUME OPTIMIZATION
# ============================================================

st.divider()

st.header(
    "Resume Optimization"
)


if st.session_state.analysis_result is None:

    st.info(
        "Run resume analysis first to enable optimization."
    )

else:

    st.write(
        "Optimize the resume using the evidence-grounded "
        "optimization pipeline."
    )

    if st.button(
        "Optimize Resume",
        type="primary",
        use_container_width=True,
    ):

        try:

            with st.spinner(
                "Optimizing resume and recalculating match score..."
            ):

                optimization_result = run_optimization(
                    api_url=api_url,
                    resume_profile=(
                        st.session_state.resume_profile
                    ),
                    resume_text=(
                        st.session_state.resume_text
                    ),
                    job_profile=(
                        st.session_state.job_profile
                    ),
                    job_text=(
                        st.session_state.job_text
                    ),
                )

            st.session_state.optimization_result = (
                optimization_result
            )

            st.success(
                "Resume optimization completed successfully."
            )

        except requests.RequestException as exc:

            st.error(
                f"Optimization request failed: {exc}"
            )

        except Exception as exc:

            st.error(
                f"Optimization failed: {exc}"
            )


# ============================================================
# OPTIMIZATION RESULTS
# ============================================================

if st.session_state.optimization_result:

    optimization_result = (
        st.session_state.optimization_result
    )


    st.divider()

    st.header(
        "Before vs After"
    )


    comparison = optimization_result[
        "comparison"
    ]

    before_score = float(
        comparison["before_score"]
    )

    after_score = float(
        comparison["after_score"]
    )

    absolute_improvement = float(
        comparison["absolute_improvement"]
    )

    percentage_improvement = float(
        comparison["percentage_improvement"]
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Before",
            f"{before_score:.2f}%",
        )


    with col2:

        st.metric(
            "After",
            f"{after_score:.2f}%",
            delta=f"{absolute_improvement:+.2f}",
        )


    with col3:

        st.metric(
            "Improvement",
            f"{absolute_improvement:+.2f}",
        )


    with col4:

        st.metric(
            "Improvement %",
            f"{percentage_improvement:+.2f}%",
        )


    # --------------------------------------------------------
    # ACCEPTANCE STATUS
    # --------------------------------------------------------

    st.subheader(
        "Optimization Status"
    )


    if optimization_result[
        "optimization_accepted"
    ]:

        st.success(
            "Optimization accepted because the final "
            "match score did not decrease."
        )

    else:

        st.warning(
            "Optimization was rejected because it reduced "
            "the overall match score. The original resume "
            "remains the final resume."
        )


    # --------------------------------------------------------
    # COMPONENT CHANGES
    # --------------------------------------------------------

    component_deltas = comparison.get(
        "component_deltas",
        {},
    )

    if component_deltas:

        st.subheader(
            "Component Score Changes"
        )

        for component, delta in (
            component_deltas.items()
        ):

            label = component.replace(
                "_",
                " ",
            ).title()

            st.write(
                f"**{label}:** {float(delta):+.2f}"
            )


    # --------------------------------------------------------
    # FINAL RESUME
    # --------------------------------------------------------

    st.subheader(
        "Final Resume"
    )

    final_resume = optimization_result[
        "final_resume"
    ]

    with st.expander(
        "View final resume"
    ):

        st.json(
            final_resume
        )


    # --------------------------------------------------------
    # OPTIMIZATION SUGGESTIONS
    # --------------------------------------------------------

    st.subheader(
        "Optimization Suggestions"
    )

    optimization_details = (
        optimization_result.get(
            "optimization",
            {},
        )
    )

    suggestions = (
        optimization_details.get(
            "suggestions",
            [],
        )
    )


    if suggestions:

        for suggestion in suggestions:

            st.write(
                f"- {suggestion}"
            )

    else:

        st.info(
            "No additional optimization suggestions."
        )


    # --------------------------------------------------------
    # KEYWORD ANALYSIS
    # --------------------------------------------------------

    keyword_analysis = (
        optimization_details.get(
            "keyword_analysis"
        )
    )

    if keyword_analysis:

        st.subheader(
            "Keyword Analysis"
        )

        keyword_col1, keyword_col2 = (
            st.columns(2)
        )


        with keyword_col1:

            st.write(
                "### Matched Keywords"
            )

            matched_keywords = (
                keyword_analysis.get(
                    "matched_keywords",
                    [],
                )
            )

            if matched_keywords:

                for keyword in matched_keywords:

                    st.success(
                        keyword
                    )

            else:

                st.info(
                    "No matched keywords listed."
                )


        with keyword_col2:

            st.write(
                "### Missing Keywords"
            )

            missing_keywords = (
                keyword_analysis.get(
                    "missing_keywords",
                    [],
                )
            )

            if missing_keywords:

                for keyword in missing_keywords:

                    st.error(
                        keyword
                    )

            else:

                st.success(
                    "No missing keywords listed."
                )


    # --------------------------------------------------------
    # DOWNLOAD FINAL RESUME
    # --------------------------------------------------------

    st.subheader(
        "Download Final Resume"
    )


    try:

        docx_content = export_docx(
            api_url=api_url,
            resume_profile=final_resume,
        )

        st.download_button(
            label="Download Final Resume (.docx)",
            data=docx_content,
            file_name="final_resume.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True,
        )

    except requests.RequestException as exc:

        st.error(
            f"Resume export failed: {exc}"
        )


# ============================================================
# JOB RECOMMENDATIONS
# ============================================================

st.divider()

st.header(
    "Job Recommendations"
)


if st.session_state.resume_profile is None:

    st.info(
        "Analyze a resume first to enable job recommendations."
    )

else:

    st.write(
        "Upload multiple job descriptions and rank them "
        "against the current resume."
    )


    # --------------------------------------------------------
    # MULTIPLE JOB UPLOAD
    # --------------------------------------------------------

    recommendation_files = st.file_uploader(
        "Upload Multiple Job Descriptions",
        type=[
            "pdf",
            "docx",
            "json",
            "txt",
        ],
        accept_multiple_files=True,
        key="recommendation_jobs",
        help=(
            "Upload multiple PDF, DOCX, JSON, or TXT job descriptions."
        ),
    )


    if recommendation_files:

        st.info(
            f"{len(recommendation_files)} job description(s) selected."
        )


        selected_job_names = [
            uploaded_file.name
            for uploaded_file
            in recommendation_files
        ]


        with st.expander(
            "Selected Job Descriptions"
        ):

            for index, name in enumerate(
                selected_job_names,
                start=1,
            ):

                st.write(
                    f"{index}. {name}"
                )


    # --------------------------------------------------------
    # RANK JOBS BUTTON
    # --------------------------------------------------------

    if st.button(
        "Rank Jobs",
        use_container_width=True,
    ):

        if not recommendation_files:

            st.warning(
                "Please upload at least one job description."
            )

        else:

            try:

                jobs = []
                job_texts = []


                with st.spinner(
                    "Processing and ranking jobs..."
                ):

                    for index, uploaded_file in enumerate(
                        recommendation_files,
                        start=1,
                    ):

                        text, job_profile = (
                            extract_job_from_upload(
                                uploaded_file
                            )
                        )


                        # Give each job a stable unique ID
                        job_profile[
                            "job_id"
                        ] = (
                            f"recommendation_job_{index}"
                        )


                        jobs.append(
                            job_profile
                        )

                        job_texts.append(
                            text
                        )


                    recommendation_result = (
                        run_job_recommendations(
                            api_url=api_url,
                            resume_profile=(
                                st.session_state.resume_profile
                            ),
                            resume_text=(
                                st.session_state.resume_text
                            ),
                            jobs=jobs,
                            job_texts=job_texts,
                        )
                    )


                st.session_state.recommendation_result = (
                    recommendation_result
                )


                st.success(
                    "Job recommendations completed successfully."
                )


            except requests.RequestException as exc:

                st.error(
                    f"Recommendation API failed: {exc}"
                )

            except Exception as exc:

                st.error(
                    f"Job recommendation failed: {exc}"
                )


# ============================================================
# JOB RECOMMENDATION RESULTS
# ============================================================

if st.session_state.recommendation_result:

    recommendation_result = (
        st.session_state.recommendation_result
    )


    recommendations = (
        recommendation_result[
            "recommendations"
        ]
    )


    st.divider()

    st.header(
        "Job Ranking"
    )


    st.write(
        f"Ranked {len(recommendations)} "
        f"job description(s) based on the current resume."
    )


    # --------------------------------------------------------
    # TOP JOB
    # --------------------------------------------------------

    if recommendations:

        best_job = recommendations[0]

        st.success(
            f"Best Match: "
            f"{best_job['title']} — "
            f"{best_job['company'] or 'Company not specified'} "
            f"({float(best_job['overall_score']):.2f}%)"
        )


    # --------------------------------------------------------
    # RANKED JOBS
    # --------------------------------------------------------

    for result in recommendations:

        rank = result["rank"]

        score = float(
            result["overall_score"]
        )

        title = result["title"]

        company = (
            result["company"]
            or "Company not specified"
        )


        st.subheader(
            f"#{rank} — {title}"
        )


        job_col1, job_col2, job_col3 = (
            st.columns(3)
        )


        with job_col1:

            st.metric(
                "Match Score",
                f"{score:.2f}%",
            )


        with job_col2:

            st.write(
                "**Company**"
            )

            st.write(
                company
            )


        with job_col3:

            st.write(
                "**Job ID**"
            )

            st.write(
                result["job_id"]
            )


        with st.expander(
            f"View details — {title}"
        ):

            # ----------------------------------------------
            # SCORE BREAKDOWN
            # ----------------------------------------------

            st.write(
                "### Score Breakdown"
            )

            breakdown = result[
                "breakdown"
            ]

            if isinstance(
                breakdown,
                dict,
            ):

                breakdown_col1, breakdown_col2 = (
                    st.columns(2)
                )

                breakdown_items = list(
                    breakdown.items()
                )

                for index, (
                    component,
                    component_score,
                ) in enumerate(
                    breakdown_items
                ):

                    current_column = (
                        breakdown_col1
                        if index % 2 == 0
                        else breakdown_col2
                    )

                    with current_column:

                        label = component.replace(
                            "_",
                            " ",
                        ).title()

                        st.metric(
                            label,
                            f"{float(component_score):.2f}",
                        )


            # ----------------------------------------------
            # MATCHED / MISSING SKILLS
            # ----------------------------------------------

            skill_match = result[
                "skill_match"
            ]

            if isinstance(
                skill_match,
                dict,
            ):

                skill_col1, skill_col2 = (
                    st.columns(2)
                )


                with skill_col1:

                    st.write(
                        "### Matched Skills"
                    )

                    matched = skill_match.get(
                        "matched",
                        [],
                    )

                    if matched:

                        for skill in matched:

                            st.success(
                                skill
                            )

                    else:

                        st.info(
                            "No matched skills."
                        )


                with skill_col2:

                    st.write(
                        "### Missing Skills"
                    )

                    missing = skill_match.get(
                        "missing",
                        [],
                    )

                    if missing:

                        for skill in missing:

                            st.error(
                                skill
                            )

                    else:

                        st.success(
                            "No missing skills."
                        )


            # ----------------------------------------------
            # STRENGTHS
            # ----------------------------------------------

            st.write(
                "### Strengths"
            )

            strengths = result[
                "strengths"
            ]

            if strengths:

                for strength in strengths:

                    st.write(
                        f"- {strength}"
                    )

            else:

                st.info(
                    "No strengths identified."
                )


            # ----------------------------------------------
            # WEAKNESSES
            # ----------------------------------------------

            st.write(
                "### Weaknesses"
            )

            weaknesses = result[
                "weaknesses"
            ]

            if weaknesses:

                for weakness in weaknesses:

                    st.write(
                        f"- {weakness}"
                    )

            else:

                st.info(
                    "No major weaknesses identified."
                )


            # ----------------------------------------------
            # RECOMMENDATIONS
            # ----------------------------------------------

            st.write(
                "### Recommendations"
            )

            job_recommendations = result[
                "recommendations"
            ]

            if job_recommendations:

                for recommendation in (
                    job_recommendations
                ):

                    st.write(
                        f"- {recommendation}"
                    )

            else:

                st.info(
                    "No additional recommendations."
                )