from sqlalchemy import Column, Boolean, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)  
    is_active = Column(Boolean(), default=True)
    created_at = Column(DateTime, default=datetime.now())
    
    articles = relationship("Article", back_populates="author")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    
    articles = relationship("Article", back_populates="category")

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)  
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    image_url = Column(String(500))  # Ссылка на изображение в MinIO/S3
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    
    category = relationship("Category", back_populates="articles")
    author = relationship("User", back_populates="articles")

class DeletedArticle(Base):
    __tablename__ = 'deleted_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_id = Column(Integer, nullable=False)  # ID из оригинальной таблицы
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    category_id = Column(Integer, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    image_url = Column(String(500))
    is_published = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, default=datetime.now())