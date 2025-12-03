import pytest
from datetime import timedelta
from jose import jwt
from security import create_access_token
from settings import SECRET_KEY, ALGORITHM


class TestSecurity:
    """Тесты для модуля безопасности"""
    
    def test_create_access_token(self):
        """Тест создания JWT токена"""
        data = {"sub": "test@example.com", "user_id": "123"}
        
        token = create_access_token(data)
        
        # Проверяем, что токен создан
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Декодируем и проверяем данные
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["sub"] == data["sub"]
        assert payload["user_id"] == data["user_id"]
        assert "exp" in payload
    
    def test_create_access_token_with_expires(self):
        """Тест создания токена с кастомным временем жизни"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=15)
        
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload