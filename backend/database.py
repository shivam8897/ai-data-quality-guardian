import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/qualitydb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_migrations():
    migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    migration_files = sorted([
        f for f in os.listdir(migrations_dir) if f.endswith(".sql")
    ])
    with engine.connect() as conn:
        for migration_file in migration_files:
            filepath = os.path.join(migrations_dir, migration_file)
            with open(filepath, "r") as f:
                sql = f.read()
            conn.execute(text(sql))
            conn.commit()
            print(f"[DB] Ran migration: {migration_file}")
