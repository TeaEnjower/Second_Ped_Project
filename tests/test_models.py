import pytest
from pydantic import ValidationError
from api.models import UserCreate, CategoryCreate, ArticleCreate


class TestModels:
    """Тесты для Pydantic моделей"""
    
    def test_user_create_valid(self):
        """Тест валидных данных пользователя"""
        user_data = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "test@example.com",
            "password": "Password123"
        }
        
        user = UserCreate(**user_data)
        
        assert user.name == "Иван"
        assert user.surname == "Иванов"
        assert user.email == "test@example.com"
        assert user.password == "Password123"
    
    def test_user_create_invalid_email(self):
        """Тест некорректного email"""
        user_data = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "invalid-email",
            "password": "Password123"
        }
        
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_category_create_valid(self):
        """Тест валидных данных категории"""
        category_data = {
            "name": "Технологии",
            "slug": "technology",
            "description": "Статьи о технологиях"
        }
        
        category = CategoryCreate(**category_data)
        
        assert category.name == "Технологии"
        assert category.slug == "technology"
        assert category.description == "Статьи о технологиях"
    
    def test_article_create_valid(self):
        """Тест валидных данных статьи"""
        article_data = {
            "title": "Тестовая статья",
            "content": "Содержание статьи",
            "excerpt": "Краткое описание",
            "category_id": 1,
            "image_url": "https://example.com/image.jpg",
            "is_published": True
        }
        
        article = ArticleCreate(**article_data)
        
        assert article.title == "Тестовая статья"
        assert article.content == "Содержание статьи"
        assert article.category_id == 1
        assert article.is_published is True