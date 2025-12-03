import pytest


@pytest.mark.asyncio
class TestUserRegistration:
    async def test_user_registration_success(self, client):
        """Тестирует успешную регистрацию пользователя."""
        response = client.post(
            "/user/",
            json={
                "name": "Марк",
                "surname": "Жуков",
                "email": "mark.zhukov@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["name"] == "Марк"
        assert data["surname"] == "Жуков"
        assert data["email"] == "mark.zhukov@example.com"
        assert data["is_active"] is True
        assert isinstance(data["created_at"], str)

    async def test_user_registration_duplicate_email(self, client):
        """Тестирует попытку регистрации с уже существующим email."""
        # Сначала зарегистрируем пользователя
        client.post(
            "/user/",
            json={
                "name": "Марк",
                "surname": "Жуков",
                "email": "duplicate@example.com",
                "password": "password456",
            },
        )

        # Попробуем зарегистрировать снова
        response = client.post(
            "/user/",
            json={
                "name": "Марк",
                "surname": "Жуков",
                "email": "duplicate@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 400
        assert "User with this email already exists" in response.json()["detail"]

    async def test_user_registration_invalid_name(self, client):
        """Тестирует регистрацию с некорректным именем."""
        response = client.post(
            "/user/",
            json={
                "name": "123",
                "surname": "Жуков",
                "email": "invalid_name@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 422  # Validation error

    async def test_user_registration_invalid_surname(self, client):
        """Тестирует регистрацию с некорректной фамилией."""
        response = client.post(
            "/user/",
            json={
                "name": "Марк",
                "surname": "123",
                "email": "invalid_surname@example.com",
                "password": "password456",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestUserLogin:
    async def test_login_success(self, client, test_user):
        """Тестирует успешный вход."""
        response = client.post(
            "/auth/login",
            data={"username": test_user["email"], "password": test_user["password"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, test_user):
        """Тестирует вход с неверным паролем."""
        response = client.post(
            "/auth/login",
            data={"username": test_user["email"], "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_wrong_email(self, client):
        """Тестирует вход с несуществующим email."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestCategoryHandlers:
    async def test_create_category_success(self, authenticated_client):
        """Тестирует создание категории."""
        response = authenticated_client.post(
            "/category/",
            json={
                "name": "Новая категория",
                "slug": "new-category",
                "description": "Описание новой категории",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Новая категория"
        assert data["slug"] == "new-category"
        assert data["description"] == "Описание новой категории"
        assert isinstance(data["id"], int)
        assert isinstance(data["created_at"], str)

    async def test_create_category_duplicate_slug(
        self, authenticated_client, test_category
    ):
        """Тестирует создание категории с дублирующимся slug."""
        response = authenticated_client.post(
            "/category/",
            json={
                "name": "Дубликат",
                "slug": test_category.slug,
                "description": "Это дубликат",
            },
        )
        assert response.status_code == 400
        assert "Category with this slug already exists" in response.json()["detail"]

    async def test_get_all_categories(self, authenticated_client):
        """Тестирует получение всех категорий."""
        response = authenticated_client.get("/category/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            first = data[0]
            assert "id" in first
            assert "name" in first
            assert "slug" in first
            assert "created_at" in first

    async def test_get_category_by_id(self, authenticated_client, test_category):
        """Тестирует получение категории по ID."""
        response = authenticated_client.get(f"/category/{test_category.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name
        assert data["slug"] == test_category.slug

    async def test_get_category_by_id_not_found(self, authenticated_client):
        """Тестирует получение несуществующей категории."""
        response = authenticated_client.get("/category/999999")
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_delete_category_success(self, authenticated_client, test_category):
        """Тестирует удаление категории."""
        response = authenticated_client.delete(f"/category/{test_category.id}")
        assert response.status_code == 200
        assert "Category deleted successfully" in response.json()["message"]

    async def test_delete_category_not_found(self, authenticated_client):
        """Тестирует удаление несуществующей категории."""
        response = authenticated_client.delete("/category/999999")
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]


@pytest.mark.asyncio
class TestArticleHandlers:
    async def test_create_article_success(self, authenticated_client, test_category):
        """Тестирует создание статьи."""
        response = authenticated_client.post(
            "/article/",
            json={
                "title": "Заголовок статьи",
                "content": "Текст статьи",
                "category_id": test_category.id,
                "excerpt": "Краткое содержание",
                "image_url": "https://example.com/image.jpg",
                "is_published": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Заголовок статьи"
        assert data["content"] == "Текст статьи"
        assert data["category_id"] == test_category.id
        assert (
            data["author_id"] == "test-uuid"
        )  # Замените на реальный user_id если нужно
        assert data["is_published"] is True
        assert isinstance(data["id"], int)
        assert isinstance(data["created_at"], str)

    async def test_create_article_category_not_found(self, authenticated_client):
        """Тестирует создание статьи с несуществующей категорией."""
        response = authenticated_client.post(
            "/article/",
            json={
                "title": "Статья без категории",
                "content": "Текст",
                "category_id": 999999,
                "is_published": True,
            },
        )
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_get_all_articles(self, authenticated_client):
        """Тестирует получение списка статей."""
        response = authenticated_client.get("/article/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "articles" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        if len(data["articles"]) > 0:
            first = data["articles"][0]
            assert "id" in first
            assert "title" in first
            assert "content" in first
            assert "category_id" in first
            assert "author_id" in first

    async def test_get_article_by_id(self, authenticated_client, test_article):
        """Тестирует получение статьи по ID."""
        article_id = test_article["id"]
        response = authenticated_client.get(f"/article/{article_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == test_article["title"]
        assert data["content"] == test_article["content"]

    async def test_get_article_by_id_not_found(self, authenticated_client):
        """Тестирует получение несуществующей статьи."""
        response = authenticated_client.get("/article/999999")
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_update_article_success(self, authenticated_client, test_article):
        """Тестирует обновление статьи."""
        article_id = test_article["id"]
        response = authenticated_client.put(
            f"/article/{article_id}",
            json={"title": "Обновленный заголовок", "content": "Обновленный текст"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == "Обновленный заголовок"
        assert data["content"] == "Обновленный текст"

    async def test_update_article_forbidden(self, client, test_article):
        """Тестирует попытку обновить чужую статью."""
        # Создаем другого пользователя
        response = client.post(
            "/user/",
            json={
                "name": "Другой",
                "surname": "Пользователь",
                "email": "other@example.com",
                "password": "password789",
            },
        )
        assert response.status_code == 200
        other_user = response.json()

        # Логинимся под ним
        login_response = client.post(
            "/auth/login",
            data={"username": other_user["email"], "password": "password789"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"

        # Пытаемся обновить статью другого пользователя
        article_id = test_article["id"]
        response = client.put(
            f"/article/{article_id}", json={"title": "Попытка взлома"}
        )
        assert response.status_code == 403
        assert "You can only update your own articles" in response.json()["detail"]

    async def test_delete_article_success(self, authenticated_client, test_article):
        """Тестирует удаление статьи."""
        article_id = test_article["id"]
        response = authenticated_client.delete(f"/article/{article_id}")
        assert response.status_code == 200
        assert "Article deleted successfully" in response.json()["message"]

    async def test_delete_article_forbidden(self, client, test_article):
        """Тестирует попытку удалить чужую статью."""
        # Создаем другого пользователя
        response = client.post(
            "/user/",
            json={
                "name": "Другой",
                "surname": "Пользователь",
                "email": "other@example.com",
                "password": "password789",
            },
        )
        assert response.status_code == 200
        other_user = response.json()

        # Логинимся под ним
        login_response = client.post(
            "/auth/login",
            data={"username": other_user["email"], "password": "password789"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"

        # Пытаемся удалить статью другого пользователя
        article_id = test_article["id"]
        response = client.delete(f"/article/{article_id}")
        assert response.status_code == 403
        assert "You can only delete your own articles" in response.json()["detail"]


@pytest.mark.asyncio
class TestEmailSending:
    async def test_test_email_endpoint(self, authenticated_client):
        """Тестирует эндпоинт для отправки тестовых email."""
        response = authenticated_client.post(
            "/user/test-email", params={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email_task_id" in data
        assert "test_task_id" in data
        assert "queues" in data
        assert "emails" in data["queues"]
        assert "default" in data["queues"]

    # Дополнительно: можно добавить тест на проверку, что задача действительно была отправлена в очередь.
    # Но это требует интеграции с Celery и может быть сложнее.
