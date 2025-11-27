from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import UserCreate, ShowUser
from db.dals import UserDAL
from db.session import get_db

user_router = APIRouter()

async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            
            existing_user = await user_dal.get_user_by_email(body.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=body.password  
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            )

@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)

@user_router.post("/login")
async def login_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    return {"message": "Login endpoint - to be implemented"}