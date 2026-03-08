import json
from dataclasses import dataclass

from app.models.course_project import CourseProject
from app.schemas.course_state import CourseState


GLOBAL_PROMPT_PROTOCOL = """
You are an education-domain AI agent in a multi-agent orchestration system.
Always return one valid JSON object only.
No markdown, no code fences, no explanatory preface.
Follow exact field names and enum values from the schema.
If information is missing, apply the Missing Value Policy and record assumptions.
""".strip()

MISSING_VALUE_POLICY = """
Missing value policy:
- Must ask before generation: subject, grade_level/target_users, duration_minutes, core teaching goal.
- Can assume conservatively: teaching_style, interaction preference, output tone.
- Never fabricate textbook version, institution policy, or exam scope.
""".strip()

LENGTH_POLICY = """
Length policy:
- clarification_questions: 3 to 5
- plan_options: 2 to 3
- strengths/risks: 2 to 4 each
- teaching_flow: 4 to 8 steps for a standard lesson
- in_class_exercises: 3 to 5
- after_class_homework: 2 to 4
""".strip()

STYLE_POLICY = """
Style policy:
- Use practical classroom language.
- Keep teacher-facing text concise, actionable, and professional.
""".strip()

REPAIR_POLICY = """
Repair strategy:
- Return one valid JSON object only.
- Remove extra keys and fill missing keys with conservative defaults.
""".strip()

STAGE_TRANSITION_RULES = """
Stage transition rules:
- clarification -> ideation only when core context is known or safely inferable.
- ideation -> confirmation only when options are concrete enough to compare.
- confirmation -> generation only after plan selection.
- generation -> qc after major content is available.
- qc -> delivery only when no blocking issue remains.
""".strip()


@dataclass(frozen=True)
class PromptSpec:
    agent: str
    stage: str
    system_prompt: str
    user_prompt: str
    output_schema: dict[str, object]
    response_format: dict[str, str]
    max_tokens: int


def build_co_creation_prompt(course_state: CourseState, message: str) -> PromptSpec:
    user_prompt = _runtime_payload(
        stage="clarification",
        payload={
            "course_state": course_state.model_dump(),
            "message": message,
        },
    )
    return PromptSpec(
        agent="course_co_creation",
        stage="clarification",
        system_prompt=_join_parts(
            [
                GLOBAL_PROMPT_PROTOCOL,
                MISSING_VALUE_POLICY,
                LENGTH_POLICY,
                STYLE_POLICY,
                "Prioritize high-value clarification questions first.",
            ]
        ),
        user_prompt=user_prompt,
        output_schema={
            "assistant_reply": "string",
            "next_question": "string",
            "clarification_questions": ["string"],
            "assumptions": ["string"],
        },
        response_format={"type": "json_object"},
        max_tokens=700,
    )


def build_instructional_design_prompt(course: CourseProject) -> PromptSpec:
    user_prompt = _runtime_payload(
        stage="ideation",
        payload={
            "course": _course_payload(course),
            "target_goal": "generate plan options",
        },
    )
    return PromptSpec(
        agent="instructional_design",
        stage="ideation",
        system_prompt=_join_parts(
            [
                GLOBAL_PROMPT_PROTOCOL,
                MISSING_VALUE_POLICY,
                LENGTH_POLICY,
                STYLE_POLICY,
                "Each plan option must differ in at least 2 dimensions: teaching style, participation pattern, preparation complexity, assessment approach.",
            ]
        ),
        user_prompt=user_prompt,
        output_schema={
            "items": [
                {
                    "id": "string",
                    "label": "string",
                    "strengths": ["string"],
                    "risks": ["string"],
                }
            ]
        },
        response_format={"type": "json_object"},
        max_tokens=900,
    )


def build_lesson_plan_prompt(course: CourseProject) -> PromptSpec:
    user_prompt = _runtime_payload(
        stage="generation",
        payload={
            "course": _course_payload(course),
            "target_goal": "build one lesson plan",
        },
    )
    return PromptSpec(
        agent="lesson_plan",
        stage="generation",
        system_prompt=_join_parts(
            [
                GLOBAL_PROMPT_PROTOCOL,
                LENGTH_POLICY,
                STYLE_POLICY,
                "teacher_script should sound like real classroom speech and stay concise.",
                "Prefer 4 to 8 teaching steps for a standard single lesson.",
            ]
        ),
        user_prompt=user_prompt,
        output_schema={
            "meta": {"topic": "string", "subject": "string", "grade": "string"},
            "objectives": ["string"],
            "timeline": [{"phase": "string", "minutes": "int"}],
            "teacher_script": ["string"],
            "board_plan": "string",
            "exercises": ["string"],
        },
        response_format={"type": "json_object"},
        max_tokens=1600,
    )


def build_quality_prompt(output: dict, grade: str) -> PromptSpec:
    user_prompt = _runtime_payload(
        stage="qc",
        payload={
            "grade": grade,
            "lesson_plan": output,
        },
    )
    return PromptSpec(
        agent="quality_gate",
        stage="qc",
        system_prompt=_join_parts(
            [
                GLOBAL_PROMPT_PROTOCOL,
                STYLE_POLICY,
                "Scoring reference: 90-100 ready to deliver, 75-89 revise, below 75 major revision.",
                "final_recommendation must be one of: 可直接交付, 建议微调后交付, 需修改后再质检",
            ]
        ),
        user_prompt=user_prompt,
        output_schema={
            "passed": "bool",
            "issues": ["string"],
            "quality_score": "int",
            "final_recommendation": "string",
        },
        response_format={"type": "json_object"},
        max_tokens=900,
    )


def build_orchestrator_prompt(course: CourseProject, message: str) -> PromptSpec:
    user_prompt = _runtime_payload(
        stage=course.stage,
        payload={
            "course": _course_payload(course),
            "message": message,
        },
    )
    return PromptSpec(
        agent="orchestrator",
        stage=course.stage,
        system_prompt=_join_parts(
            [
                GLOBAL_PROMPT_PROTOCOL,
                MISSING_VALUE_POLICY,
                STAGE_TRANSITION_RULES,
                REPAIR_POLICY,
                "The orchestrator controls state transitions; child agents generate content only.",
            ]
        ),
        user_prompt=user_prompt,
        output_schema={
            "next_stage": "string",
            "missing_fields": ["string"],
            "message_to_user": "string",
            "assumptions": ["string"],
        },
        response_format={"type": "json_object"},
        max_tokens=800,
    )


def _runtime_payload(stage: str, payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "Runtime Injection (JSON):",
            json.dumps({"stage": stage, **payload}, ensure_ascii=False),
        ]
    )


def _course_payload(course: CourseProject) -> dict[str, object]:
    return {
        "id": course.id,
        "topic": course.topic,
        "subject": course.subject,
        "grade": course.grade,
        "duration": course.duration,
        "stage": course.stage,
        "selected_option_id": course.selected_option_id,
    }


def _join_parts(parts: list[str]) -> str:
    return "\n\n".join(part.strip() for part in parts if part.strip())
