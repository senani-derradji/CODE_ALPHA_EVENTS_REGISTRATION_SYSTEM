from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserCreateResponse
from app.services.user_service import UserOperations
from app.depend.current_user import get_current_user, required_admin, required_organization, required_user_or_admin
from app.services.EMAIL_SERVICE.notification_service import NotificationService
from app.utils.validate_user_token import validate_activation_token, create_activation_token


router = APIRouter()
notification = NotificationService()


@router.post("/create/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_ops = UserOperations(db)
    created_user = await user_ops.create_user(user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Failed to create user")

    try:
        await notification.send_account_activated_email(
        recipient_email=created_user.get("email"),
        user_name=created_user.get("username"),
        token=await create_activation_token(created_user.get("user_id"))
        )
    except Exception as e:
        print(e)

    return UserCreateResponse(
        id=created_user.get("user_id"),
        username=created_user.get("username"),
        email=created_user.get("email"),
        role=created_user.get("role"),
        access_token=created_user.get("access_token"),
        token_type=created_user.get("token_type"),
        is_active=True if created_user.get("is_active") else False
    )

# Admin only: Get all users
@router.get("/get_users/", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin = Depends(required_admin)
):
    user_ops = UserOperations(db)
    return await user_ops.get_users(skip, limit)

# Admin or Self: Get specific user
@router.get("/get_user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Allow if user is admin or is accessing their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    user_ops = UserOperations(db)
    user = await user_ops.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Admin or Self: Update user
@router.put("/update_user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Allow if user is admin or is updating their own profile
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user_ops = UserOperations(db)
    updated_user = await user_ops.update_user(user_id, **user.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# Admin only: Delete user
@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(required_admin)
):
    user_ops = UserOperations(db)
    deleted_user = await user_ops.delete_user(user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# Admin or Organization: Promote user to organization role
@router.put("/promote_to_organization/{user_id}", response_model=UserResponse)
async def promote_to_organization(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(required_admin)
):
    user_ops = UserOperations(db)
    updated_user = await user_ops.update_user(user_id, role="organization")
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user