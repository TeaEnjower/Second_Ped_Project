from db.session import get_db
import asyncpg 
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import settings

test_engine = create_async_engine(settings.REAL_DATABASE_URL_TEST, future=True, echo=True)
async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)