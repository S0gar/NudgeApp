import asyncio

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from backend.db.database import create_db_and_tables, session_factory
from backend.db.models import UserBase, TasksBase

create_db_and_tables()


# ПЕРЕПИСАТЬ ТУТ ВСЕ ФУНКЦИИ

# def create_user(user: UserBase, session) -> None:
#     session.add(user)

async def create_user(tg_id:int, user_name: str, users_time_zone: int = 7):
    async with session_factory() as session:
        user = UserBase(
                telegram_id=tg_id,
                user_name=user_name,
                time_zone=users_time_zone)
        session.add(user)
        await session.commit()
        return user

async def delete_user(user: UserBase, session) -> UserBase:
    async with session_factory() as session:
        session.delete(user)
        await session.commit()
        return user

# Вспомогательная функция для get_by
async def _get_user_by(raise_if_none: bool = False, **kwargs) -> UserBase | None:
    async with session_factory() as session:
        # filter_by позволяет удобно искать по переданным аргументам (например, id=1)
        stmt = select(UserBase).filter_by(**kwargs)
        
        # session.scalar() вернет первый найденный объект или None
        db_object = await session.scalar(stmt)
        
        if raise_if_none and db_object is None:
            raise NoResultFound(f"User with parameters {kwargs} not found.")
            
        return db_object

async def get_by_id(id: int) -> UserBase:
    return await _get_user_by(raise_if_none=True, id=id)

async def try_to_get_by_id(id: int) -> UserBase | None:
    return await _get_user_by(raise_if_none=False, id=id)

async def get_by_tg_id(tg_id: int) -> UserBase:
    return await _get_user_by(raise_if_none=True, telegram_id=tg_id)

async def try_to_get_by_tg_id(tg_id: int) -> UserBase | None:
    return await _get_user_by(raise_if_none=False, telegram_id=tg_id)


async def create_task(user_id:int, title: str, text: str, deadline: str, status: str = "active") -> TasksBase:
    async with session_factory() as session:
        task = TasksBase(user_id=user_id, title=title, text=text, deadline=deadline, status=status)
        session.add(task)
        await session.commit()
        return task


async def _get_tasks_by(raise_if_none: bool = False, **kwargs) -> TasksBase | None:
    async with session_factory() as session:
        stmt = select(TasksBase).filter_by(**kwargs)
        db_obj = await session.scalars(stmt)

        if raise_if_none and db_obj is None:
            raise(f"Tasks with parameters {kwargs} not found.")

        return db_obj

async def get_user_tasks_by_id(user_id: int) -> list[TasksBase]:
    return await _get_tasks_by(raise_if_none=True, id=user_id)

async def try_get_user_tasks_by_id(user_id: int) -> list[TasksBase] | None:
    return await _get_tasks_by(raise_if_none=False, id=user_id)

async def get_task_by_id(task_id: int) -> TasksBase:
    return await _get_tasks_by(raise_if_none=True, id=task_id)

async def try_get_task_by_id(task_id: int) -> TasksBase | None:
    return await _get_tasks_by(raise_if_none=False, id=task_id)


async def delete_task(task: TasksBase) -> None:
    async with session_factory() as session:
        session.delete(task)
        await session.commit()

async def delete_task_by_id(task_id: int) -> None:
    task = await get_task_by_id(task_id=task_id)
    return await delete_task(task) 
