# tests/conftest.py
import pytest
from typing import Generator
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from main import app
from db.session import get_db
from security import create_access_token


@pytest.fixture(scope="function")
def mock_db_session() -> AsyncMock:
    """Мок сессии базы данных"""
    session = AsyncMock(spec=AsyncSession)
    
    # Настраиваем async context manager
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    
    # Настраиваем begin() как async context manager
    session.begin.return_value.__aenter__.return_value = session
    session.begin.return_value.__aexit__.return_value = None
    
    # Настраиваем execute() для возврата мокового результата
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result
    
    return session


@pytest.fixture(scope="function")
def client(mock_db_session: AsyncMock) -> Generator:
    """Фикстура для тестового клиента FastAPI"""
    
    async def override_get_db():
        yield mock_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data() -> dict:
    return {
        "name": "Иван",
        "surname": "Иванов",
        "email": "test@example.com",
        "password": "TestPassword123"
    }


@pytest.fixture(scope="function")
def mock_user():
    """Мок пользователя с правильными типами данных"""
    user = Mock()
    user.user_id = uuid.uuid4()
    user.name = "Иван"
    user.surname = "Иванов"
    user.email = "test@example.com"
    user.hashed_password = "hashed_password_123"
    user.is_active = True
    user.created_at = datetime.now()  # Должен быть datetime объект
    return user


@pytest.fixture(scope="function")
def mock_category():
    """Мок категории"""
    category = Mock()
    category.id = 1
    category.name = "Технологии"
    category.slug = "technology"
    category.description = "Статьи о технологиях"
    category.created_at = datetime.now()  # Должен быть datetime объект
    return category


@pytest.fixture(scope="function")
def mock_article(mock_user, mock_category):
    """Мок статьи"""
    article = Mock()
    article.id = 1
    article.title = "Тестовая статья"
    article.content = "Содержание"
    article.excerpt = "Краткое описание"
    article.category_id = mock_category.id
    article.author_id = mock_user.user_id
    article.image_url = "https://example.com/image.jpg"
    article.is_published = True
    article.created_at = datetime.now()
    article.updated_at = datetime.now()
    return article


@pytest.fixture(scope="function")
def auth_token(mock_user) -> str:
    return create_access_token(
        data={"sub": mock_user.email, "user_id": str(mock_user.user_id)}
    )