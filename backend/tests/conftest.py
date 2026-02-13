import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.base import Base
from app.infrastructure.db.session import get_db
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_db
from app.infrastructure.security.auth import get_password_hash
from app.main import app

engine = create_engine("sqlite+pysqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def seed_users():
    db = TestingSessionLocal()
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123"), role="admin"))
        db.add(User(username="viewer", hashed_password=get_password_hash("viewer123"), role="viewer"))
        db.commit()
    db.close()


seed_users()
client = TestClient(app)
