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
