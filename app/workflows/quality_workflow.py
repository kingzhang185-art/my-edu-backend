from app.agents.quality_agent import collect_quality_issues


def run_quality_check(output: dict, grade: str) -> dict:
    issues = collect_quality_issues(output=output, grade=grade)
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "quality_score": max(0, 100 - len(issues) * 20),
        "fix_suggestions": [f"fix:{issue}" for issue in issues],
    }
