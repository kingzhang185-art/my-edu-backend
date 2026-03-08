from app.schemas.course_state import CourseState


def test_state_patch_merge():
    base = CourseState(topic="分数加减法", subject="数学", grade="四年级", duration=40)
    patch = {"teaching_style": "互动型", "deliverables": ["教案"]}
    merged = base.model_copy(update=patch)

    assert merged.teaching_style == "互动型"
    assert merged.deliverables == ["教案"]
