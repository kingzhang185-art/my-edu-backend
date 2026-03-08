from app.agents.co_creation_agent import get_prompt_spec as get_co_creation_prompt
from app.agents.lesson_plan_agent import get_prompt_spec as get_lesson_plan_prompt
from app.agents.orchestrator import AgentOrchestrator
from app.agents.quality_agent import get_prompt_spec as get_quality_prompt
from app.agents.teaching_design_agent import get_prompt_spec as get_teaching_design_prompt
from app.models.course_project import CourseProject
from app.schemas.course_state import CourseState
from app.services.deliverable_service import get_deliverable_service
from app.services.generation_service import get_generation_service


def _sample_course(stage: str = "draft") -> CourseProject:
    return CourseProject(
        id="1",
        topic="分数加减法",
        subject="数学",
        grade="四年级",
        duration=40,
        stage=stage,
    )


def test_child_agents_use_json_prompt_protocol():
    state = CourseState(topic="分数加减法", subject="数学", grade="四年级", duration=40)
    course = _sample_course()

    co_creation_prompt = get_co_creation_prompt(state, "我要备课")
    design_prompt = get_teaching_design_prompt(course)
    lesson_prompt = get_lesson_plan_prompt(course)
    quality_prompt = get_quality_prompt({"teacher_script": []}, "四年级")

    assert co_creation_prompt.response_format == {"type": "json_object"}
    assert design_prompt.response_format == {"type": "json_object"}
    assert lesson_prompt.response_format == {"type": "json_object"}
    assert quality_prompt.response_format == {"type": "json_object"}

    assert "clarification_questions: 3 to 5" in co_creation_prompt.system_prompt
    assert "teaching_flow: 4 to 8 steps" in lesson_prompt.system_prompt
    assert "final_recommendation must be one of" in quality_prompt.system_prompt


def test_orchestrator_prompt_contains_stage_transition_rules():
    orchestrator = AgentOrchestrator(
        generation_service=get_generation_service(),
        deliverable_service=get_deliverable_service(),
    )
    prompt = orchestrator.get_prompt_spec(_sample_course(stage="clarifying"), "继续")

    assert prompt.agent == "orchestrator"
    assert prompt.stage == "clarifying"
    assert "Stage transition rules" in prompt.system_prompt
    assert "qc -> delivery only when no blocking issue remains" in prompt.system_prompt
