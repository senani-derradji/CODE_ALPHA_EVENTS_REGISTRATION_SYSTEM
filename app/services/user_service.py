from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.security.hash import create_password_hash
from fastapi import HTTPException, status
from app.security.jwt import create_access_token
import re
from app.utils.validate_user_token import validate_activation_token, create_activation_token


class UserOperations:

    def __init__(self, db: Session = None):
        if db is None:
            self.db = next(get_db())
        else:
            self.db = db

    def create_user(self, data: UserCreate):
        username = data.username
        email = data.email
        password = data.password


        if self.get_user_by_email(email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if self.get_user_by_username(username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        db_user = User(username=username, email=email, password=create_password_hash(password), is_active=0)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        access_token = create_access_token(data={"sub": db_user.username})

        return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id, "username": db_user.username, "email": db_user.email, "role": db_user.role}

    def create_oauth_user(self, username: str, email: str, password: str):
        base = re.sub(r"[^a-zA-Z0-9_.-]", "_", username)[:40]
        final_username = base
        counter = 1
        user = self.get_user_by_username(final_username)


        while user:
            final_username = f"{base}_{counter}"
            counter += 1

        db_user = User(username=final_username, email=email, password=create_password_hash(password), is_active=1)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def count_users(self) -> int:
        return self.db.query(User).count()

    def count_users_by_role(self, role: str) -> int:
        return self.db.query(User).filter(User.role == role).count()

    def update_user(self, user_id: int, **kwargs):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        new_username = kwargs.get("username")
        if new_username and db_user.username != new_username and self.get_user_by_username(new_username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        new_email = kwargs.get("email")
        if new_email and db_user.email != new_email and self.get_user_by_email(new_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        if kwargs.get("password"):
            kwargs["password"] = create_password_hash(kwargs["password"])

        if "role" not in kwargs:
            if db_user.updated_times is None:
                db_user.updated_times = 0
            if db_user.updated_times >= 5:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum profile update limit reached")
            db_user.updated_times = (db_user.updated_times or 0) + 1

        for key, value in kwargs.items():
            setattr(db_user, key, value)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.db.delete(db_user)
        self.db.commit()
        return {"deleted": True}
