# tests/test_middleware.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock


class TestMiddleware:
    """Упрощенные тесты middleware"""
    
    def test_public_routes_access(self, client: TestClient):
        """Тест доступа к публичным маршрутам"""
        # GET запросы должны работать
        response = client.get("/docs")
        assert response.status_code in [200, 301]
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        response = client.get("/category/")
        # Может быть 200 или 500 (если нет моков), но не 401/403 от middleware
        assert response.status_code != 401
        assert response.status_code != 403
    
    def test_protected_route_without_auth(self, client: TestClient):
        """Тест защищенного маршрута без авторизации"""
        # POST /category/ требует авторизации
        category_data = {
            "name": "Технологии",
            "slug": "technology",
            "description": "Статьи о технологиях"
        }
        
        response = client.post("/category/", json=category_data)
        
        # Должна быть ошибка 403 (Forbidden) или 401 (Unauthorized)
        # Проверяем что это ошибка аутентификации/авторизации
        assert response.status_code in [401, 403]
    
   