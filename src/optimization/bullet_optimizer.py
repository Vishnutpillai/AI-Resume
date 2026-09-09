from app.schemas.resume import Project


def optimize_bullet(
    bullet: str,
    relevant_keywords: list[str],
) -> str:
    """
    Improve a resume bullet using only information already present
    in the original bullet.

    No achievements, metrics, technologies, or experience are invented.
    """

    if not bullet or not bullet.strip():
        return bullet

    text = bullet.strip()

    # Remove weak opening phrases.
    weak_starts = [
        "worked on ",
        "responsible for ",
        "worked with ",
        "helped with ",
        "involved in ",
        "did ",
    ]

    lower_text = text.lower()

    for phrase in weak_starts:
        if lower_text.startswith(phrase):
            text = text[len(phrase):].strip()
            break

    # Capitalize first character.
    if text:
        text = text[0].upper() + text[1:]

    # Add a period if missing.
    if text and text[-1] not in ".!?":
        text += "."

    return text


def optimize_project_bullet(
    project: Project,
    relevant_keywords: list[str],
) -> str:
    """
    Convert a project description into a stronger resume bullet
    without adding unsupported claims.
    """

    description = project.description or ""

    optimized = optimize_bullet(
        description,
        relevant_keywords,
    )

    technologies = [
        tech.strip()
        for tech in project.technologies
        if tech.strip()
    ]

    # Only append technologies that already belong to the project.
    if technologies:
        tech_text = ", ".join(technologies)

        if tech_text.lower() not in optimized.lower():
            optimized = (
                f"{optimized.rstrip('.')} "
                f"using {tech_text}."
            )

    return optimized