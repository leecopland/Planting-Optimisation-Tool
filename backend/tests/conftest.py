import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: F401
from httpx import AsyncClient, ASGITransport

# --- Application Imports ---
from src.config import Settings
from src.database import Base
from src.dependencies import create_access_token
from src.models.user import User
from src.models.soil_texture import SoilTexture
from src.main import app
from src.models.agroforestry_type import AgroforestryType
from src.schemas.constants import SoilTextureID, AgroforestryTypeID

settings = Settings()


# Event Loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database Engine
@pytest.fixture(scope="function")
async def db_engine():
    """Provides a single, asynchronous database engine for the session."""
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    # Dispose of the engine resources after all tests run
    await engine.dispose()


# Database Setup/Teardown Fixture
@pytest.fixture(scope="function", autouse=True)
async def setup_database(db_engine):
    """
    Creates all tables before any test runs and drops them after all tests complete.
    """
    async with db_engine.begin() as conn:
        # Create all tables defined in Base.metadata
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        # Drop all tables after all tests are complete
        await conn.run_sync(Base.metadata.drop_all)


# Transactional Session Fixture
@pytest.fixture(scope="function")
async def async_session(db_engine):
    """
    Provides a transactional async session that guarantees a clean database state
    for every single test function by rolling back the transaction afterward.
    """
    # Acquire a connection and start a transaction block
    async with db_engine.begin() as conn:
        # Bind a session to the connection/transaction
        session = AsyncSession(conn, expire_on_commit=False)

        try:
            # Yield the session to the test function
            yield session
        finally:
            # Close the session
            await session.close()
            # Rollback the transaction to discard all changes made during the test
            await conn.rollback()


@pytest.fixture(scope="function")
async def async_client(async_session):
    """HTTP client forced to use the test's transactional session."""

    # We define a nested function that FastAPI will call.
    # It simply returns the session object provided by the pytest fixture.
    async def _get_test_db():
        yield async_session

    # Link the override to your project's dependency name
    app.dependency_overrides[get_db_session] = _get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up after the test so production code isn't affected
    app.dependency_overrides.clear()


# User Fixtures
@pytest.fixture(scope="function")
async def test_user_a(async_session: AsyncSession) -> User:
    """Fixture for creating User A (Owner) and persisting them."""
    user = User(
        name="Alice Owner", email="alice.test@farm.com", hashed_password="secure_hash_a"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_user_b(async_session: AsyncSession) -> User:
    """Fixture for creating User B (Intruder)."""
    user = User(
        name="Bob Intruder", email="bob.test@farm.com", hashed_password="secure_hash_b"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def setup_soil_texture(async_session: AsyncSession):
    """Ensures a SoilTexture record exists with a known ID for Farm FK constraints."""
    texture = SoilTexture(id=1, name="Test Loam")
    async_session.add(texture)
    await async_session.commit()
    await async_session.refresh(texture)
    return texture


# Authorization Header Fixtures
@pytest.fixture(scope="function")
def auth_user_headers(test_user_a: User) -> dict:
    """Provides Authorization headers (JWT) for User A."""
    access_token = create_access_token(
        data={"sub": str(test_user_a.id)}
    )  # Use ID as sub
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def auth_user_b_headers(test_user_b: User) -> dict:
    """Provides Authorization headers (JWT) for User B."""
    access_token = create_access_token(
        data={"sub": str(test_user_b.id)}
    )  # Use ID as sub
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def seed_constants(async_session: AsyncSession):
    """
    Seeds the reference tables required for Pydantic FK validation
    and model relationships.
    """
    # Seed Soil Textures from Enum
    for entry in SoilTextureID:
        async_session.add(SoilTexture(id=entry.value, name=entry.name.lower()))

    # Seed Agroforestry Types from Enum
    for entry in AgroforestryTypeID:
        async_session.add(
            AgroforestryType(id=entry.value, type_name=entry.name.lower())
        )

    await async_session.commit()
