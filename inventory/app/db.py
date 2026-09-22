import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = (
    "postgresql+psycopg://{user}:{password}@{host}:{port}/{name}".format(
        user=os.getenv("DB_USER", "synapseshop"),
        password=os.getenv("DB_PASSWORD", "synapseshop"),
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        name=os.getenv("DB_NAME", "synapseshop"),
    )
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass