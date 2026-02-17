from app.infrastructure.db.models import User
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.security.auth import get_password_hash


def bootstrap_users() -> None:
    db = SessionLocal()
    try:
        default_users = [
            ("admin", "admin123", "admin"),
            ("viewer", "viewer123", "viewer"),
        ]
        for username, password, role in default_users:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                db.add(User(username=username, hashed_password=get_password_hash(password), role=role))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    bootstrap_users()
