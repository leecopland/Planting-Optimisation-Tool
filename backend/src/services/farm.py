from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.schemas.farm import FarmCreate
from src.models import Farm
from src.models import User


async def create_farm_record(db: AsyncSession, farm_data: FarmCreate, user_id: int):
    """
    Creates a new Farm record in the database.
    """
    # Prepare the data
    farm_data_dict = farm_data.model_dump()

    # Add the Foreign Key
    farm_data_dict["user_id"] = user_id

    # Create the ORM object
    db_farm = Farm(**farm_data_dict)

    # 4. Add to session and commit
    db.add(db_farm)
    await db.commit()

    # Refresh the object (essential for getting the new ID and relationships)
    await db.refresh(db_farm)

    return db_farm


async def get_farm_by_id(
    db: AsyncSession, farm_id: int, current_user: User
) -> Farm | None:
    """
    Retrieves a single Farm record, filtered by farm_id AND user_id
    to enforce ownership authorization.

    Includes selectinload for relationships to prevent MissingGreenlet errors
    during Pydantic serialization.
    """
    user_id_int = current_user.id

    # We add .options(selectinload(...)) for every relationship
    # that the FarmRead schema needs to display.
    stmt = (
        select(Farm)
        .options(selectinload(Farm.soil_texture), selectinload(Farm.agroforestry_type))
        .where((Farm.id == farm_id) & (Farm.user_id == user_id_int))
    )

    result = await db.execute(stmt)

    return result.scalars().first()
