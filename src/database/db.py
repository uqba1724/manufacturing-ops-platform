import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Check if Azure SQL credentials are available
# If yes, use Azure SQL. If no, fall back to SQLite.
AZURE_SERVER = os.getenv("AZURE_SQL_SERVER")
AZURE_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")

if AZURE_SERVER and AZURE_PASSWORD:
    # Azure SQL Database connection
    # pymssql is the Python driver for Microsoft SQL Server
    DATABASE_URL = (
        f"mssql+pymssql://ecamadmin:{AZURE_PASSWORD}"
        f"@{AZURE_SERVER}/ecam-manufacturing-db"
        
    )
    print("Using Azure SQL Database")
else:
    # Local SQLite fallback
    DATABASE_URL = "sqlite:///./data/manufacturing.db"
    print("Using local SQLite database")

engine = create_engine(
    DATABASE_URL,
    # connect_args only needed for SQLite
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()