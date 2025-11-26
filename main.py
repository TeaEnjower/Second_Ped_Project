from fastapi import FastAPI
import settings
import uvicorn
from fastapi.routing import APIRouter
from sqlalchemy import Column, Boolean, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
import re 
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr
from pydantic import field_validator


engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

class TuneModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ShowUser(TuneModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool

class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Name should contain only letters")
        return value
    
    @field_validator("surname")
    @classmethod
    def validate_surname(cls, value: str) -> str:  # ← уникальное имя метода
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Surname should contain only letters")
        return value
    
app = FastAPI(title="Marketplace")

user_router = APIRouter()

async def _create_new_user(body: UserCreate) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )
        

@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)


main_api_router = APIRouter()

main_api_router.include_router(user_router, prefix='/user', tags=['user'])
app.include_router(main_api_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000 )