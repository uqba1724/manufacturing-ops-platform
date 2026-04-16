from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# This is the path to our SQLite database file.
# It will be created automatically when we run init_db.py.
DATABASE_URL = "sqlite:///./data/manufacturing.db"

# The engine is the connection to the database.
# connect_args is needed for SQLite to allow multiple threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for creating database sessions.
# A session is a temporary conversation with the database
# where you can read and write data.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base is the parent class all our table models will inherit from.
# SQLAlchemy uses it to track which classes represent tables.
Base = declarative_base()


def get_db():
    # This function creates a session, hands it to whoever needs it,
    # and closes it cleanly when they are done.
    # Used later by FastAPI to inject a database session into endpoints.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()