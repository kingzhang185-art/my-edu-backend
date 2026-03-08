from app.agents.quality_agent import build_final_recommendation, collect_quality_issues


def run_quality_check(output: dict, grade: str) -> dict:
    issues = collect_quality_issues(output=output, grade=grade)
    score = max(0, 100 - len(issues) * 20)
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "quality_score": score,
        "final_recommendation": build_final_recommendation(score),
        "fix_suggestions": [f"fix:{issue}" for issue in issues],
    }
