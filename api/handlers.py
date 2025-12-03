from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from api.models import (
    UserCreate,
    ShowUser,
    CategoryCreate,
    ShowCategory,
    ArticleCreate,
    ArticleUpdate,
    ShowArticle,
    ArticleListResponse,
)
from db.dals import UserDAL, CategoryDAL, ArticleDAL
from db.session import get_db
from hashed import Hashed
from security import get_current_user
from worker.tasks import send_welcome_email


user_router = APIRouter()
category_router = APIRouter()
article_router = APIRouter()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)

            existing_user = await user_dal.get_user_by_email(body.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists",
                )

            hashed_password = Hashed.get_password_hash(body.password)

            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
                hashed_password=hashed_password,
            )

            # Подготовка данных для email
            user_data = {
                "user_id": str(user.user_id),
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }

            # Асинхронный вызов задачи Celery
            try:
                # Отправляем задачу в очередь
                task = send_welcome_email.delay(user_data)

                # Логируем для отладки
                print("✅ Задача отправки email поставлена в очередь:")
                print(f"   ID задачи: {task.id}")
                print(f"   Для пользователя: {user.email}")
                print("   Очередь: emails")

                # Можно сохранить task.id в БД для отслеживания

            except Exception as e:
                # Логируем ошибку, но не прерываем регистрацию
                print(f"⚠️ Ошибка постановки задачи в очередь: {str(e)}")
                print("Регистрация пользователя завершена, но email не отправлен")

            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
            )


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)


@category_router.post("/", response_model=ShowCategory)
async def create_category(
    body: CategoryCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShowCategory:
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(session)

            existing_category = await category_dal.get_category_by_slug(body.slug)
            if existing_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this slug already exists",
                )

            category = await category_dal.create_category(
                name=body.name, slug=body.slug, description=body.description
            )

            return ShowCategory(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                created_at=category.created_at,
            )


@category_router.get("/", response_model=list[ShowCategory])
async def get_all_categories(db: AsyncSession = Depends(get_db)):
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(session)
            categories = await category_dal.get_all_categories()

            return [
                ShowCategory(
                    id=category.id,
                    name=category.name,
                    slug=category.slug,
                    description=category.description,
                    created_at=category.created_at,
                )
                for category in categories
            ]


@category_router.get("/{category_id}", response_model=ShowCategory)
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(session)
            category = await category_dal.get_category_by_id(category_id)

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

            return ShowCategory(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                created_at=category.created_at,
            )


@category_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db as session:
        async with session.begin():
            category_dal = CategoryDAL(session)

            category = await category_dal.get_category_by_id(category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

            success = await category_dal.delete_category(category_id)

            if success:
                return {"message": "Category deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete category",
                )


@article_router.post("/", response_model=ShowArticle)
async def create_article(
    body: ArticleCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShowArticle:
    async with db as session:
        async with session.begin():
            article_dal = ArticleDAL(session)
            category_dal = CategoryDAL(session)

            category = await category_dal.get_category_by_id(body.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

            article = await article_dal.create_article(
                title=body.title,
                content=body.content,
                excerpt=body.excerpt,
                category_id=body.category_id,
                author_id=current_user["user_id"],
                image_url=body.image_url,
                is_published=body.is_published,
            )

            return ShowArticle(
                id=article.id,
                title=article.title,
                content=article.content,
                excerpt=article.excerpt,
                category_id=article.category_id,
                author_id=article.author_id,
                image_url=article.image_url,
                is_published=article.is_published,
                created_at=article.created_at,
                updated_at=article.updated_at,
            )


@article_router.get("/", response_model=ArticleListResponse)
async def get_all_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    async with db as session:
        async with session.begin():
            article_dal = ArticleDAL(session)

            if category_id:
                articles = await article_dal.get_articles_by_category(category_id)
                articles = articles[skip : skip + limit]
                total = len(await article_dal.get_articles_by_category(category_id))
            else:
                articles = await article_dal.get_all_articles(skip=skip, limit=limit)
                total = await article_dal.get_articles_count()

            return ArticleListResponse(
                articles=[
                    ShowArticle(
                        id=article.id,
                        title=article.title,
                        content=article.content,
                        excerpt=article.excerpt,
                        category_id=article.category_id,
                        author_id=article.author_id,
                        image_url=article.image_url,
                        is_published=article.is_published,
                        created_at=article.created_at,
                        updated_at=article.updated_at,
                    )
                    for article in articles
                ],
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                page_size=limit,
                total_pages=(total + limit - 1) // limit if limit > 0 else 1,
            )


@article_router.get("/{article_id}", response_model=ShowArticle)
async def get_article_by_id(article_id: int, db: AsyncSession = Depends(get_db)):
    async with db as session:
        async with session.begin():
            article_dal = ArticleDAL(session)
            article = await article_dal.get_article_by_id(article_id)

            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
                )

            return ShowArticle(
                id=article.id,
                title=article.title,
                content=article.content,
                excerpt=article.excerpt,
                category_id=article.category_id,
                author_id=article.author_id,
                image_url=article.image_url,
                is_published=article.is_published,
                created_at=article.created_at,
                updated_at=article.updated_at,
            )


@article_router.put("/{article_id}", response_model=ShowArticle)
async def update_article(
    article_id: int,
    body: ArticleUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db as session:
        async with session.begin():
            article_dal = ArticleDAL(session)

            article = await article_dal.get_article_by_id(article_id)
            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
                )

            if str(article.author_id) != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own articles",
                )

            if body.category_id:
                category_dal = CategoryDAL(session)
                category = await category_dal.get_category_by_id(body.category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found",
                    )

            updated_article = await article_dal.update_article(
                article_id, **body.model_dump(exclude_unset=True)
            )

            return ShowArticle(
                id=updated_article.id,
                title=updated_article.title,
                content=updated_article.content,
                excerpt=updated_article.excerpt,
                category_id=updated_article.category_id,
                author_id=updated_article.author_id,
                image_url=updated_article.image_url,
                is_published=updated_article.is_published,
                created_at=updated_article.created_at,
                updated_at=updated_article.updated_at,
            )


@article_router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db as session:
        async with session.begin():
            article_dal = ArticleDAL(session)

            article = await article_dal.get_article_by_id(article_id)
            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
                )

            if str(article.author_id) != current_user["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own articles",
                )

            success = await article_dal.delete_article(article_id)

            if success:
                return {"message": "Article deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete article",
                )


@user_router.post("/test-email")
async def test_email_send(
    email: str = Query(..., description="Email для тестовой отправки"),
    db: AsyncSession = Depends(get_db),
):
    """
    Тестовый endpoint для проверки отправки email
    """
    from worker.tasks import send_welcome_email, test_email_task

    test_data = {
        "user_id": "test-uuid",
        "name": "Тестовый",
        "surname": "Пользователь",
        "email": email,
        "created_at": "2024-01-01T00:00:00",
    }

    # Отправляем тестовую задачу
    task1 = send_welcome_email.delay(test_data)
    task2 = test_email_task.delay(email)

    return {
        "message": "Тестовые задачи отправлены в очередь",
        "email_task_id": task1.id,
        "test_task_id": task2.id,
        "queues": ["emails", "default"],
    }
