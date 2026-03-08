from app.agents.prompt_protocol import PromptSpec, build_quality_prompt
from app.services.model_gateway import get_model_gateway

_ALLOWED_RECOMMENDATIONS = {"可直接交付", "建议微调后交付", "需修改后再质检"}


def collect_quality_issues(output: dict, grade: str) -> list[str]:
    issues: list[str] = []

    banned_phrases = ["你太笨了", "真差劲", "别问了"]
    script_lines = output.get("teacher_script", [])
    script_blob = "\n".join(script_lines)
    for phrase in banned_phrases:
        if phrase in script_blob:
            issues.append(f"unsafe_phrase:{phrase}")

    required_sections = ["timeline", "teacher_script"]
    for section in required_sections:
        if section not in output:
            issues.append(f"missing_section:{section}")

    if "幼" in grade and output.get("difficulty") == "advanced":
        issues.append("age_mismatch:advanced_for_preschool")

    return issues


def build_final_recommendation(score: int) -> str:
    if score >= 90:
        return "可直接交付"
    if score >= 75:
        return "建议微调后交付"
    return "需修改后再质检"


def get_prompt_spec(output: dict, grade: str) -> PromptSpec:
    return build_quality_prompt(output=output, grade=grade)


def evaluate_quality(output: dict, grade: str) -> dict | None:
    spec = get_prompt_spec(output=output, grade=grade)
    payload = get_model_gateway().generate_json(spec)
    return _parse_quality_payload(payload)


def _parse_quality_payload(payload: dict) -> dict | None:
    if not isinstance(payload, dict):
        return None

    passed = payload.get("passed")
    if not isinstance(passed, bool):
        return None

    raw_issues = payload.get("issues", [])
    if not isinstance(raw_issues, list):
        return None
    issues = [issue for issue in raw_issues if isinstance(issue, str) and issue.strip()]

    raw_score = payload.get("quality_score")
    if isinstance(raw_score, bool):
        return None
    if isinstance(raw_score, (int, float)):
        score = int(raw_score)
    else:
        return None
    score = max(0, min(100, score))

    raw_recommendation = payload.get("final_recommendation")
    if isinstance(raw_recommendation, str) and raw_recommendation in _ALLOWED_RECOMMENDATIONS:
        recommendation = raw_recommendation
    else:
        recommendation = build_final_recommendation(score)

    return {
        "passed": passed,
        "issues": issues,
        "quality_score": score,
        "final_recommendation": recommendation,
    }
