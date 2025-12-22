from sqlalchemy.ext.asyncio import AsyncSession

# Models

# Data science packages
from suitability_scoring import (
    score_farms_species_by_id_list,
    build_species_params_dict,
    build_species_recommendations,
)
import pandas as pd


async def run_recommendation_pipeline(db: AsyncSession, farms, all_species, cfg):
    # Convert DB objects to DataFrames (Engine Requirement)
    # Map Farm object to dict for DataFrame
    farms_data = []
    for f in farms:
        farms_data.append(
            {
                "farm_id": f.id,
                "rainfall_mm": f.rainfall_mm,
                "ph": float(f.ph),
                "temperature_celsius": f.temperature_celsius,
                "elevation_m": f.elevation_m,
                "soil_texture": f.soil_texture.name.lower() if f.soil_texture else None,
            }
        )
    farms_df = pd.DataFrame(farms_data)

    # Species are already coming in as dicts from get_all_species_for_engine
    species_df = pd.DataFrame(all_species)

    # Build Params Index
    # using empty DF for now because no overrides, using recommend.yaml instead
    empty_params_df = pd.DataFrame(
        columns=["species_id", "feature", "score_method", "weight"]
    )
    params_index = build_species_params_dict(empty_params_df, cfg)

    # Define the exclusion logic
    # For now, we allow all species as valid candidates
    all_ids = species_df["species_id"].tolist()

    def provider(farm_row):
        return all_ids

    # Run the engine function
    scores_df, explanations = score_farms_species_by_id_list(
        farms_df=farms_df,
        species_df=species_df,
        cfg=cfg,
        get_valid_tree_ids=provider,
        params_index=params_index,
    )

    # Format for the API response
    batch_results = []
    for farm_id in farms_df["farm_id"].unique():
        farm_explanations = explanations.get(farm_id, [])
        # build_species_recommendations handles sorting/formatting
        formatted_recs = build_species_recommendations(farm_explanations)

        batch_results.append({"farm_id": farm_id, "recommendations": formatted_recs})

    return batch_results
