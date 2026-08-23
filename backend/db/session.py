from sqlalchemy.orm import session
from sqlalchemy import select

from backend.db.database import engine, create_db_and_tables
from backend.db.models import UserBase

Session = session.sessionmaker(engine)

Igor = UserBase(telegram_id=14543534543, user_name="s0gar")

create_db_and_tables()


def create_user(user: UserBase, session) -> None:
    session.add(user)

def get_by_id(telegram_id, session) -> list[UserBase]:
    statement = select(UserBase).where(UserBase.telegram_id == telegram_id)
    db_object = session.scalars(statement).one()
    return db_object

def delete_user(user: UserBase, session) -> UserBase:
    session.delete(user)
    return user
