import asyncio  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from src.models.farm import Farm
from suitability_scoring.recommend import build_payload_for_farm  # noqa: F401


async def get_recommendations_for_farm(db: AsyncSession, farm_id: int):
    """
    Orchestrates the recommendation generation.
    TODO: Need to update recommend.build_payload_for_farm to be async and DB-aware.
    """
    # Verification that farm exists
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    # Logic
    try:
        return
        # Once TODO is done, uncomment below.

        # return await build_payload_for_farm(db, farm_id)
        # recommendations = await asyncio.to_thread(build_payload_for_farm, db, farm_id)
        # return recommendations
    except TypeError:
        raise Exception
