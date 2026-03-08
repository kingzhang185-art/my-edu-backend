from app.agents.templates import build_plan_template


def test_preschool_plan_has_game_and_operation():
    plan = build_plan_template(segment="preschool", subject="启蒙数学")
    assert "游戏" in "".join(plan["activities"])
    assert "操作" in "".join(plan["activities"])


def test_k12_plan_has_practice():
    plan = build_plan_template(segment="k12", subject="数学")
    assert any("练" in activity for activity in plan["activities"])
