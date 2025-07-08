from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = None
        self.async_session_maker = None

    async def init(self):
        DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///ads.db')
        self.engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для логов SQL
        self.async_session_maker = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        return self.async_session_maker()

    async def close(self):
        if self.engine:
            await self.engine.dispose()


# Глобальный экземпляр базы данных
db = Database()