from sqlalchemy.orm.session import sessionmaker

from backend.db.database import create_db_and_tables, engine

create_db_and_tables()

session_factory = sessionmaker(engine)