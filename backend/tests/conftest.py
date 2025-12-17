import sys
import os
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: F401
from httpx import AsyncClient, ASGITransport

# --- Application Imports ---
from src.config import Settings
from src.database import Base
from src.dependencies import create_access_token
from src.models.user import User
from src.models.soil_texture import SoilTexture
from src.main import app

# Manual path adjustment to ensure 'src' is importable when running from a subdirectory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

settings = Settings()


# --- Fixture 1: Event Loop ---
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# --- Fixture 2: Database Engine (Session Scope) ---
@pytest.fixture(scope="function")
async def db_engine():
    """Provides a single, asynchronous database engine for the session."""
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    # Dispose of the engine resources after all tests run
    await engine.dispose()


# --- 3. Database Setup/Teardown Fixture (Function Scope, Autoused) ---
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


# --- 4. Transactional Session Fixture (Function Scope - Guarantees Isolation) ---
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


# --- 5. Application Client Fixture (NEW) ---
@pytest.fixture(scope="function")
async def async_client():
    """HTTP client connected to the FastAPI application."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# --- 6. User Fixtures (NEW) ---
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
    # This fixture correctly commits the data, so no change needed here.
    texture = SoilTexture(id=1, name="Test Loam")
    async_session.add(texture)
    await async_session.commit()
    await async_session.refresh(texture)
    return texture


# --- 7. Authorization Header Fixtures (NEW) ---
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
