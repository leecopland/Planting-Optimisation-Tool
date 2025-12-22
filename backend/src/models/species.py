# Species table model and reference tables
from sqlalchemy import ForeignKey
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .soil_texture import SoilTexture
    from .agroforestry_type import AgroforestryType
from .association import (
    species_agroforestry_association,
    species_soil_texture_association,
)


class Species(Base):
    __tablename__ = "species"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    common_name: Mapped[str] = mapped_column()
    rainfall_mm_min: Mapped[int] = mapped_column()
    rainfall_mm_max: Mapped[int] = mapped_column()
    temperature_celsius_min: Mapped[int] = mapped_column()
    temperature_celsius_max: Mapped[int] = mapped_column()
    elevation_m_min: Mapped[int] = mapped_column()
    elevation_m_max: Mapped[int] = mapped_column()
    ph_min: Mapped[float] = mapped_column()  # 1 decimal
    ph_max: Mapped[float] = mapped_column()  # 1 decimal
    coastal: Mapped[bool] = mapped_column()
    riparian: Mapped[bool] = mapped_column()
    nitrogen_fixing: Mapped[bool] = mapped_column()
    shade_tolerant: Mapped[bool] = mapped_column()
    bank_stabilising: Mapped[bool] = mapped_column()

    # Relationships
    # -------------
    # Links a species object to its corresponding soil_texture object
    soil_textures: Mapped[list["SoilTexture"]] = relationship(
        secondary=species_soil_texture_association,
        back_populates="soil_textures_for_species",
    )

    # Links a species object to its corresponding agroforestry_type object
    agroforestry_types: Mapped[list["AgroforestryType"]] = relationship(
        secondary=species_agroforestry_association,
        back_populates="species_agroforestry_type",
    )

    def to_dict(self):
        # Extract the names of the soil textures into a list of strings
        # For recommendation logic - this matches what the DS engine expects for categorical scoring
        soil_names = [st.name.lower() for st in self.soil_textures]

        return {
            "id": self.id,
            "name": self.name,
            "common_name": self.common_name,
            "rainfall_mm_min": self.rainfall_mm_min,
            "rainfall_mm_max": self.rainfall_mm_max,
            "ph_min": self.ph_min,
            "ph_max": self.ph_max,
            "temperature_celsius_min": self.temperature_celsius_min,
            "temperature_celsius_max": self.temperature_celsius_max,
            "elevation_m_min": self.elevation_m_min,
            "elevation_m_max": self.elevation_m_max,
            "preferred_soil_texture": soil_names,
            "coastal": self.coastal,
            "riparian": self.riparian,
            "nitrogen_fixing": self.nitrogen_fixing,
            "shade_tolerant": self.shade_tolerant,
            "bank_stabilising": self.bank_stabilising,
        }

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Species object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Species(id={self.id!r}, name{self.name!r}, common_name{self.common_name!r})"
