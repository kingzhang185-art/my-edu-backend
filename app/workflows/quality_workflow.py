from app.agents.quality_agent import (
    build_final_recommendation,
    collect_quality_issues,
    evaluate_quality,
)


def run_quality_check(output: dict, grade: str) -> dict:
    model_result = evaluate_quality(output=output, grade=grade)
    if model_result is not None:
        issues = model_result["issues"]
        score = model_result["quality_score"]
        return {
            "passed": model_result["passed"],
            "issues": issues,
            "quality_score": score,
            "final_recommendation": model_result["final_recommendation"],
            "fix_suggestions": [f"fix:{issue}" for issue in issues],
        }

    issues = collect_quality_issues(output=output, grade=grade)
    score = max(0, 100 - len(issues) * 20)
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "quality_score": score,
        "final_recommendation": build_final_recommendation(score),
        "fix_suggestions": [f"fix:{issue}" for issue in issues],
    }
