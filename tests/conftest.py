import os

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.db.base import Base
from app.db.session import engine


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
