import os

from sqlalchemy import create_engine
from backend.db.models import Base


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATABASE_PATH = os.path.join(CURRENT_DIR, "users.db")
engine = create_engine(f"sqlite:////{USER_DATABASE_PATH}", echo=True)


def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)
