import uuid
import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TuneModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(TuneModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Name should contain only letters")
        return value

    @field_validator("surname")
    @classmethod
    def validate_surname(cls, value: str) -> str:
        if not LETTER_MATCH_PATTERN.match(value):
            raise ValueError("Surname should contain only letters")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class ShowCategory(TuneModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime


class ArticleCreate(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None
    is_published: bool = True


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None


class ShowArticle(TuneModel):
    id: int
    title: str
    content: str
    excerpt: Optional[str]
    category_id: int
    author_id: uuid.UUID
    image_url: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[ShowCategory] = None
    author: Optional[ShowUser] = None


class ArticleListResponse(TuneModel):
    articles: list[ShowArticle]
    total: int
    page: int
    page_size: int
    total_pages: int


class TokenResponse(Token):
    pass
