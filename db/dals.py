from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, Category, Article, DeletedArticle
from sqlalchemy.orm import selectinload
import uuid


class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_user_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_users(self) -> list[User]:
        query = select(User)
        result = await self.db_session.execute(query)
        return result.scalars().all()


class CategoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_category(
        self, name: str, slug: str, description: str = None
    ) -> Category:
        new_category = Category(name=name, slug=slug, description=description)
        self.db_session.add(new_category)
        await self.db_session.flush()
        return new_category

    async def get_all_categories(self) -> list[Category]:
        query = select(Category)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_category_by_slug(self, slug: str) -> Category:
        query = select(Category).where(Category.slug == slug)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_category_by_id(self, category_id: int) -> Category:
        query = select(Category).where(Category.id == category_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def delete_category(self, category_id: int) -> bool:
        category = await self.get_category_by_id(category_id)
        if category:
            await self.db_session.delete(category)
            await self.db_session.flush()
            return True
        return False


class ArticleDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_article(
        self,
        title: str,
        content: str,
        category_id: int,
        author_id: uuid.UUID,
        excerpt: str = None,
        image_url: str = None,
        is_published: bool = True,
    ) -> Article:
        new_article = Article(
            title=title,
            content=content,
            excerpt=excerpt,
            category_id=category_id,
            author_id=author_id,
            image_url=image_url,
            is_published=is_published,
        )
        self.db_session.add(new_article)
        await self.db_session.flush()
        return new_article

    async def get_article_by_id(self, article_id: int) -> Article:
        query = (
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .where(Article.id == article_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_articles(self, skip: int = 0, limit: int = 100) -> list[Article]:
        query = (
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_articles_by_category(self, category_id: int) -> list[Article]:
        query = (
            select(Article)
            .options(selectinload(Article.category), selectinload(Article.author))
            .where(Article.category_id == category_id)
        )
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def update_article(self, article_id: int, **kwargs) -> Article:
        article = await self.get_article_by_id(article_id)
        if article:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(article, key, value)
            await self.db_session.flush()
        return article

    async def delete_article(self, article_id: int) -> bool:
        article = await self.get_article_by_id(article_id)
        if article:
            deleted_article = DeletedArticle(
                original_id=article.id,
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
            self.db_session.add(deleted_article)

            await self.db_session.delete(article)
            await self.db_session.flush()
            return True
        return False

    async def get_articles_count(self) -> int:
        query = select(Article)
        result = await self.db_session.execute(query)
        return len(result.scalars().all())
