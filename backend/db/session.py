from sqlalchemy.orm import session
from sqlalchemy import select

from backend.db.database import engine, create_db_and_tables
from backend.db.models import UserBase, TasksBase


Session = session.sessionmaker(engine)

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


def create_task(task: TasksBase, session) -> TasksBase:
    session.add(task)
    return task


def get_user_tasks(user_id: int, session) -> list[TasksBase]:
    statement = select(TasksBase).where(TasksBase.user_id == user_id)
    return list(session.scalars(statement).all())


def get_task_by_id(task_id: int, session) -> TasksBase | None:
    statement = select(TasksBase).where(TasksBase.id == task_id)
    return session.scalars(statement).first()


def delete_task(task: TasksBase, session) -> None:
    session.delete(task)
    return task
