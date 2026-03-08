from app.models.course_project import CourseProject


def generate_lesson_plan(course: CourseProject) -> dict:
    return {
        "meta": {"topic": course.topic, "subject": course.subject, "grade": course.grade},
        "timeline": [],
    }
