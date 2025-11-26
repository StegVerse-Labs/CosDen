from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .age import AgeProfile


@dataclass
class CosmeticUserProfile:
    """
    Minimal cosmetic user profile for planning.

    We deliberately keep this lightweight and non-medical.

    - age_years: coarse age for routing to age group and gating
    - tone_preference: "cool", "warm", "neutral", or None
    - sensitivity_flag: if True, planner should bias to gentler stacks
    - event_time_hours: when the user cares about looking best (None = general)
    - notes: freeform cosmetic-only notes (e.g. "coffee drinker", "photoshoot")
    """
    age_years: int
    age_profile: AgeProfile
    tone_preference: Optional[str] = None
    sensitivity_flag: bool = False
    event_time_hours: Optional[int] = None
    notes: Optional[str] = None

    @staticmethod
    def from_age(
        age_years: int,
        tone_preference: Optional[str] = None,
        sensitivity_flag: bool = False,
        event_time_hours: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> "CosmeticUserProfile":
        from .age import AgeProfile as AP  # avoid cycle

        return CosmeticUserProfile(
            age_years=age_years,
            age_profile=AP.from_age(age_years),
            tone_preference=tone_preference,
            sensitivity_flag=sensitivity_flag,
            event_time_hours=event_time_hours,
            notes=notes,
        )
