from app.agents.co_creation_agent import ask_next_question
from app.agents.orchestrator import AgentOrchestrator
from app.agents.teaching_design_agent import build_option_labels
from app.models.course_project import CourseProject
from app.schemas.course_state import CourseState
from app.services.deliverable_service import get_deliverable_service
from app.services.generation_service import get_generation_service
from app.workflows.quality_workflow import run_quality_check


class _StubGateway:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def generate_json(self, _spec) -> dict:
        return self._payload


def test_co_creation_prefers_gateway_response(monkeypatch):
    state = CourseState(topic="小学英语", subject="英语", grade="三年级", duration=40)
    monkeypatch.setattr(
        "app.agents.co_creation_agent.get_model_gateway",
        lambda: _StubGateway(
            {
                "assistant_reply": "我们先确认目标学习结果。",
                "next_question": "这节课最希望学生课后能做到什么？",
            }
        ),
    )

    result = ask_next_question(state, "我要备课")
    assert result["assistant_reply"] == "我们先确认目标学习结果。"
    assert result["next_question"] == "这节课最希望学生课后能做到什么？"


def test_teaching_design_prefers_gateway_plan_labels(monkeypatch):
    course = CourseProject(
        id="1",
        topic="分数加减法",
        subject="数学",
        grade="四年级",
        duration=40,
    )
    monkeypatch.setattr(
        "app.agents.teaching_design_agent.get_model_gateway",
        lambda: _StubGateway(
            {
                "items": [
                    {"id": "option_1", "label": "问题驱动"},
                    {"id": "option_2", "label": "探究实验"},
                    {"id": "option_3", "label": "讲练融合"},
                ]
            }
        ),
    )

    labels = build_option_labels(course)
    assert labels == ["问题驱动", "探究实验", "讲练融合"]


def test_quality_workflow_prefers_gateway_response(monkeypatch):
    monkeypatch.setattr(
        "app.agents.quality_agent.get_model_gateway",
        lambda: _StubGateway(
            {
                "passed": False,
                "issues": ["missing_section:timeline"],
                "quality_score": 65,
                "final_recommendation": "需修改后再质检",
            }
        ),
    )

    result = run_quality_check(output={"teacher_script": ["请读一读"]}, grade="三年级")
    assert result["passed"] is False
    assert result["issues"] == ["missing_section:timeline"]
    assert result["quality_score"] == 65
    assert result["final_recommendation"] == "需修改后再质检"


def test_orchestrator_exposes_gateway_stage_message(monkeypatch):
    monkeypatch.setattr(
        "app.agents.orchestrator.get_model_gateway",
        lambda: _StubGateway(
            {
                "next_stage": "clarification",
                "missing_fields": [],
                "message_to_user": "先补齐核心信息再继续。",
                "assumptions": [],
            }
        ),
    )
    orchestrator = AgentOrchestrator(
        generation_service=get_generation_service(),
        deliverable_service=get_deliverable_service(),
    )
    course = CourseProject(
        id="1",
        topic="分数加减法",
        subject="数学",
        grade="四年级",
        duration=40,
    )

    result = orchestrator.run_clarification(course, "继续")

    assert result["orchestrator_message"] == "先补齐核心信息再继续。"
