from app.agents.prompt_protocol import PromptSpec, build_quality_prompt


def collect_quality_issues(output: dict, grade: str) -> list[str]:
    _ = get_prompt_spec(output=output, grade=grade)
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
