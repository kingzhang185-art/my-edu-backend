from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.repositories.course_project_repo import SqlAlchemyCourseProjectRepo


def test_sql_course_project_repo_persists_between_instances(tmp_path):
    db_path = tmp_path / "course_repo.db"
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(engine)

    repo_a = SqlAlchemyCourseProjectRepo(session_factory)
    created = repo_a.create(topic="过去进行时", subject="英语", grade="八年级", duration=45)

    repo_b = SqlAlchemyCourseProjectRepo(session_factory)
    loaded = repo_b.get(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.topic == "过去进行时"
    assert loaded.stage == "draft"
