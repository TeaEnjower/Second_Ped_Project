from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, Category, Article, DeletedArticle

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

class CategoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_category(self, name: str, slug: str, description: str = None) -> Category:
        new_category = Category(
            name=name,
            slug=slug,
            description=description
        )
        self.db_session.add(new_category)
        await self.db_session.flush()
        return new_category

    async def get_all_categories(self) -> list[Category]:
        query = select(Category)
        result = await self.db_session.execute(query)
        return result.scalars().all()