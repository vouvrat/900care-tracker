import os
from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine

DB_PATH = os.environ.get("DB_PATH", "/data/900care.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def _migrate(session: Session) -> None:
    existing = {row[1] for row in session.exec(text("PRAGMA table_info(product)"))}
    if "image_url" not in existing:
        session.exec(text("ALTER TABLE product ADD COLUMN image_url TEXT DEFAULT ''"))
        session.commit()


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _migrate(session)


def get_session():
    with Session(engine) as session:
        yield session
