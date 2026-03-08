from app.agents.teaching_design_agent import build_option_labels
from app.models.course_project import CourseProject


def generate_plan_options(course: CourseProject) -> dict[str, list[dict[str, str]]]:
    labels = build_option_labels(course)
    items = [
        {"id": f"option_{index + 1}", "label": label}
        for index, label in enumerate(labels)
    ]
    return {"items": items}
