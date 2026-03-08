from app.models.course_project import CourseProject
from app.agents.templates import build_plan_template
from typing import cast


def generate_lesson_plan(course: CourseProject) -> dict:
    segment = _infer_segment(course.grade)
    template = build_plan_template(segment=segment, subject=course.subject)
    activities = cast(list[str], template["activities"])
    minutes = max(1, course.duration // max(1, len(activities)))
    timeline = [{"phase": activity, "minutes": minutes} for activity in activities]

    return {
        "meta": {
            "topic": course.topic,
            "subject": course.subject,
            "grade": course.grade,
            "duration": course.duration,
            "segment": segment,
        },
        "objectives": [
            f"理解{course.topic}核心概念",
            "能够在课堂活动中完成一次迁移应用",
        ],
        "key_points": [f"{course.topic}关键知识点拆解", "课堂互动反馈"],
        "timeline": timeline,
        "teacher_script": [
            f"同学们，今天我们一起学习{course.topic}。",
            "先观察示例，再分组完成任务。",
            "最后我们一起复盘关键步骤。",
        ],
        "board_plan": f"{course.topic} | 关键概念 | 示例演示 | 课堂练习",
        "exercises": [f"完成1道与{course.topic}相关的课堂练习并分享解题思路。"],
        "difficulty": "basic" if segment == "preschool" else "standard",
    }


def _infer_segment(grade: str) -> str:
    preschool_markers = ("幼", "学前", "小班", "中班", "大班")
    if any(marker in grade for marker in preschool_markers):
        return "preschool"
    return "k12"
