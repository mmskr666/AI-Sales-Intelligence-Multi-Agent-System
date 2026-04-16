from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ======================
# 你自己改成你的 PostgreSQL 连接信息
# ======================
ASYNC_DB_URL = "postgresql+asyncpg://postgres:123456@localhost:5432/postgres"

# 创建引擎
engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,  # 生产环境关闭
    future=True,
    pool_recycle=1800,
)

# 会话工厂（全局只有一个，不浪费资源）
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# ======================
# 给接口用的依赖（FastAPI注入）
# ======================
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session