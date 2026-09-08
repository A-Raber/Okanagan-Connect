from backend.DB.database import create_db_and_tables, engine
# import models so SQLModel metadata includes them
from backend.DB import models  # noqa: F401

if __name__ == "__main__":
	print("Creating database + tables at", engine.url)
	create_db_and_tables()
	print("Done.")
