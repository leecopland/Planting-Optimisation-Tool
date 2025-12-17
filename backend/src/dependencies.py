from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

from src.database import get_db_session
from src.schemas.user import UserRead
from src.services.user import get_user_by_id
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    # Use timezone-aware UTC for consistency
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # PyJWT handles the 'exp' check automatically during decode
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert the string ID from the token to integer
        user_id_int = int(user_id_str)

    except (InvalidTokenError, ValueError):
        # InvalidTokenError covers expired, malformed, or wrong-signature tokens
        raise credentials_exception
    except Exception:
        # Catch-all for other unexpected issues
        raise credentials_exception

    # Look up the user in the database
    user = await get_user_by_id(db, user_id=user_id_int)
    if user is None:
        raise credentials_exception

    return UserRead.model_validate(user)


CurrentActiveUser = Security(get_current_active_user)
