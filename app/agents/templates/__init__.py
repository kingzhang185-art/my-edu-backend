from app.agents.templates.k12_templates import K12_TEMPLATE_FAMILIES
from app.agents.templates.preschool_templates import PRESCHOOL_TEMPLATE_FAMILIES


def build_plan_template(segment: str, subject: str) -> dict[str, object]:
    normalized = segment.lower().strip()
    if normalized == "preschool":
        base = PRESCHOOL_TEMPLATE_FAMILIES["default"]
    else:
        base = K12_TEMPLATE_FAMILIES["default"]

    return {
        "segment": normalized,
        "subject": subject,
        "activities": list(base["activities"]),
        "prompt": build_segment_prompt(segment=normalized, subject=subject),
    }


def build_segment_prompt(segment: str, subject: str) -> str:
    if segment == "preschool":
        return f"请为幼教{subject}课程生成以游戏互动和操作探究为核心的活动方案。"
    return f"请为K12{subject}课程生成包含讲练结合与任务驱动的活动方案。"
