from app.models.user import User
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate
from app.security.hash import create_password_hash
from fastapi import HTTPException, status
from app.security.jwt import create_access_token
import re
from sqlalchemy import select


class UserOperations:

    def __init__(self, db: AsyncSession = None):
        if db is None:
            self.db = next(get_db())  # ⚠️ better inject via router
        else:
            self.db = db

    async def create_user(self, data: UserCreate):

        if await self.get_user_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        if await self.get_user_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already taken")

        db_user = User(
            username=data.username,
            email=data.email,
            password=await create_password_hash(data.password),
            is_active=0
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        access_token = await create_access_token({"sub": db_user.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role
        }

    async def create_oauth_user(self, username: str, email: str, password: str):

        base = re.sub(r"[^a-zA-Z0-9_.-]", "_", username)[:40]
        final_username = base
        counter = 1

        while await self.get_user_by_username(final_username):
            final_username = f"{base}_{counter}"
            counter += 1

        db_user = User(
            username=final_username,
            email=email,
            password=await create_password_hash(password),
            is_active=1
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user

    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()

    async def get_user_by_username(self, username: str):
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def get_users(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count_users(self) -> int:
        result = await self.db.execute(select(User))
        return len(result.scalars().all())

    async def count_users_by_role(self, role: str) -> int:
        result = await self.db.execute(
            select(User).where(User.role == role)
        )
        return len(result.scalars().all())

    async def update_user(self, user_id: int, **kwargs):

        db_user = await self.get_user_by_id(user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        new_username = kwargs.get("username")
        if new_username and db_user.username != new_username:
            if await self.get_user_by_username(new_username):
                raise HTTPException(status_code=400, detail="Username already taken")

        new_email = kwargs.get("email")
        if new_email and db_user.email != new_email:
            if await self.get_user_by_email(new_email):
                raise HTTPException(status_code=400, detail="Email already registered")

        # if "password" in kwargs:
        #     kwargs["password"] = await create_password_hash(kwargs["password"])

        for key, value in kwargs.items():
            setattr(db_user, key, value)

        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user

    async def delete_user(self, user_id: int):
        db_user = await self.get_user_by_id(user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        await self.db.delete(db_user)
        await self.db.commit()

        return {"deleted": True}