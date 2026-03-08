from app.workflows.quality_workflow import run_quality_check


def test_quality_gate_flags_unsafe_content():
    output = {"teacher_script": ["你太笨了，快点记住。"]}
    result = run_quality_check(output, grade="二年级")
    assert result["passed"] is False
    assert len(result["issues"]) > 0
