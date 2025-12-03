from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from db.models import Base
from main import app  # Импортируем FastAPI приложение
from db.session import get_db
from hashed import Hashed

# Для тестов используем отдельную БД
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:Daemonium_555@localhost:5432/test_db"

# Создаем движок для тестовой БД
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Фикстура для создания сессии
@pytest_asyncio.fixture(scope="session")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает и возвращает асинхронную сессию."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal(bind=conn) as session:
            yield session
            await session.rollback()
    await engine.dispose()


# Фикстура для клиента FastAPI
@pytest_asyncio.fixture(scope="session")
async def client():
    """Создает тестового клиента FastAPI."""
    from fastapi.testclient import TestClient

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with TestClient(app) as client:
        yield client


# Фикстура для тестового пользователя
@pytest_asyncio.fixture(scope="session")
async def test_user(async_session):
    """Создает тестового пользователя."""
    from db.dals import UserDAL

    user_dal = UserDAL(async_session)
    password = "password123"
    hashed_password = Hashed.get_password_hash(password)
    user = await user_dal.create_user(
        name="Тест",
        surname="Пользователь",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    await async_session.commit()
    return {
        "user_id": str(user.user_id),
        "name": "Тест",
        "surname": "Пользователь",
        "email": "test@example.com",
        "password": password,
    }


# Фикстура для авторизованного клиента
@pytest_asyncio.fixture(scope="session")
async def authenticated_client(client, test_user):
    """Возвращает клиент, авторизованный под тестовым пользователем."""
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# Фикстура для тестовой категории
@pytest_asyncio.fixture(scope="session")
async def test_category(async_session):
    """Создает тестовую категорию."""
    from db.dals import CategoryDAL

    category_dal = CategoryDAL(async_session)
    category = await category_dal.create_category(
        name="Тестовая категория",
        slug="test-category",
        description="Описание тестовой категории",
    )
    await async_session.commit()
    return category


# Фикстура для тестовой статьи
@pytest_asyncio.fixture(scope="session")
async def test_article(authenticated_client, test_category):
    """Создает тестовую статью через API."""
    response = authenticated_client.post(
        "/article/",
        json={
            "title": "Тестовая статья",
            "content": "Текст тестовой статьи",
            "category_id": test_category.id,
            "is_published": True,
        },
    )
    assert response.status_code == 200
    return response.json()
