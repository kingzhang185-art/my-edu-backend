from app.models.course_project import CourseProject
from app.agents.prompt_protocol import PromptSpec, build_instructional_design_prompt
from app.services.model_gateway import get_model_gateway


def build_option_labels(course: CourseProject) -> list[str]:
    spec = get_prompt_spec(course)
    llm_labels = _parse_llm_labels(get_model_gateway().generate_json(spec))
    if llm_labels:
        return llm_labels
    preschool_markers = ("幼", "学前", "小班", "中班", "大班")
    if any(marker in course.grade for marker in preschool_markers):
        return ["游戏互动", "绘本情境", "操作探究"]
    return ["探究式", "讲练结合", "情境任务"]


def get_prompt_spec(course: CourseProject) -> PromptSpec:
    return build_instructional_design_prompt(course)


def _parse_llm_labels(payload: dict) -> list[str]:
    items = payload.get("items")
    if not isinstance(items, list):
        return []

    labels: list[str] = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        if isinstance(label, str) and label.strip():
            labels.append(label.strip())
    return labels
