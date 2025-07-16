import asyncio
from db import engine, Base
from models.sql import User, Infrastructure
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.username == "jean"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(username="jean", password="jean")
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
        result = await session.execute(select(Infrastructure).where(Infrastructure.name == "default"))
        infra = result.scalar_one_or_none()
        if not infra:
            infra = Infrastructure(name="default", user_id=user.id)
            session.add(infra)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db()) 