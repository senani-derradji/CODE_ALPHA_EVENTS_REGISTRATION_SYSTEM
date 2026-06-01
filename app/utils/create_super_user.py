from app.models.user import User
from app.security.hash import create_password_hash
from app.core.config import settings
from app.core.database import get_db
from sqlalchemy import select


async def create_user():

    async for db in get_db():

        result = await db.execute(
            select(User).where(User.username == settings.admin_username)
        )
        existing_user = result.scalars().first()

        if existing_user:
            print("Admin user already exists, skipping creation")
            return existing_user

        user = User(
            username=settings.admin_username,
            email=settings.admin_email,
            password=await create_password_hash(settings.admin_password),
            role="admin",
            is_active=1
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"Admin user created with id: {user.id}")
        return user