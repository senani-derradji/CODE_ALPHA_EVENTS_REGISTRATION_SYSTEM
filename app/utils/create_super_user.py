from app.models.user import User
from app.security.hash import create_password_hash
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.core.config import settings


def create_user():
    db: Session = next(get_db())

    existing_user = db.query(User).filter(User.username == settings.admin_username).first()
    if existing_user:
        print("Admin user already exists, skipping creation")
        db.close()
        return existing_user

    user = User(
        username=settings.admin_username,
        email=settings.admin_email,
        password=create_password_hash(settings.admin_password),
        role="admin",
        is_active=1
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    print(f"Admin user created with id: {user.id}")
    return user