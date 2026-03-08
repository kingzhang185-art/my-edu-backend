from app.models.course_project import CourseProject


def build_option_labels(course: CourseProject) -> list[str]:
    preschool_markers = ("幼", "学前", "小班", "中班", "大班")
    if any(marker in course.grade for marker in preschool_markers):
        return ["游戏互动", "绘本情境", "操作探究"]
    return ["探究式", "讲练结合", "情境任务"]
