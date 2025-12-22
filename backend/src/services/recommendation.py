from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from suitability_scoring import (
    calculate_suitability,
    build_species_params_dict,
    build_rules_dict,
    build_species_recommendations,
)

async def run_recommendation_pipeline(db: AsyncSession, farms, all_species, cfg):
    # Build the params Index
    # Using an empty df for default YAML logic
    empty_params_df = pd.DataFrame(columns=["species_id", "feature", "score_method", "weight"])
    params_dict = build_species_params_dict(empty_params_df, cfg)
    
    # Pre-calculate the optimized rules for all species
    optimised_rules = build_rules_dict(all_species, params_dict, cfg)

    batch_results = []

    # Iterate through each farm and score
    for f in farms:
        # Prepare the single farm dictionary as the engine expects it
        farm_profile = {
            "id": f.id,
            "rainfall_mm": f.rainfall_mm,
            "ph": float(f.ph),
            "temperature_celsius": f.temperature_celsius,
            "elevation_m": f.elevation_m,
            "soil_texture": f.soil_texture.name.lower() if f.soil_texture else None,
            # If other features are added to the YAML file they need to be included here.
        }

        # Run the engine for the farm
        # result_list is the list of dicts with explanations, scores_list is for debugging
        result_list, scores_list = calculate_suitability(
            farm_data=farm_profile,
            species_list=all_species,
            optimised_rules=optimised_rules,
            cfg=cfg
        )

        # Format, rank and sort using the presentation logic
        formatted_recs = build_species_recommendations(result_list)

        batch_results.append({
            "farm_id": f.id,
            "recommendations": formatted_recs
        })

    return batch_results