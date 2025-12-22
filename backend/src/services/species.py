import os
import suitability_scoring
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from suitability_scoring.utils.config import load_yaml
from src.models.species import Species


def get_recommend_config():
    # Finds the directory where suitability_scoring is installed
    package_path = os.path.dirname(suitability_scoring.__file__)
    # Goes one level up from 'src/suitability_scoring' to find 'config/'
    base_path = os.path.dirname(package_path)
    config_path = os.path.join(base_path, "config", "recommend.yaml")

    return load_yaml(config_path)


async def get_all_species_for_engine(db: AsyncSession):
    # Loading the soil_textures relationship
    stmt = select(Species).options(selectinload(Species.soil_textures))
    result = await db.execute(stmt)
    return [sp.to_dict() for sp in result.scalars().all()]
