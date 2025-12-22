import asyncio
from sqlalchemy import text
from src.database import AsyncSessionLocal


async def check_stats():
    async with AsyncSessionLocal() as session:
        queries = {
            "Users": "SELECT count(*) FROM users",
            "Farms": "SELECT count(*) FROM farms",
            "Species": "SELECT count(*) FROM species",
            "Boundaries": "SELECT count(*) FROM boundary",
            "Soil Texture Links": "SELECT count(*) FROM species_soil_texture_association",
            "Agroforestry Links": "SELECT count(*) FROM species_agroforestry_association",
        }
        print("\n" + "=" * 30)
        print("Database population summary")
        print("=" * 30)
        for label, query in queries.items():
            try:
                res = await session.execute(text(query))
                print(f"  - {label:20}: {res.scalar()}")
            except Exception:
                print(f"  - {label:20}: Error (Table might not exist)")
        print("=" * 30 + "\n")


if __name__ == "__main__":
    asyncio.run(check_stats())
