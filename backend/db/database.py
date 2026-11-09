from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import session
from backend.db.models import Base
from backend.config import Config

engine = create_async_engine(
    Config.DB_URL, 
    echo=True)

session_factory = session.sessionmaker(engine)

def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)
