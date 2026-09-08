from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path
import os

# Ensure DB is always in backend/DB/ folder, regardless of where script is run from
db_dir = Path(__file__).resolve().parent  # c:\Users\...\backend\DB\
db_file = db_dir / "dev.db"

# Allow override via OK_DB env var
DB_URL = os.environ.get("OK_DB", f"sqlite:///{db_file}")

# create engine; check_same_thread False for sqlite + multiple sessions in single thread
engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})

def get_session():
	# yields a session for use in FastAPI deps or scripts:
	with Session(engine) as session:
		yield session

def create_db_and_tables():
	# ensure all SQLModel models are imported before calling this
	SQLModel.metadata.create_all(engine)