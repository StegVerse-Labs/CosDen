from __future__ import annotations

from typing import Dict, List

from .age import AgeProfile, AgeGroup
from .models import Product
from .goals import CosmeticGoal, CosmeticGoalType


def _filter_allowed_by_age(
    catalog: Dict[str, Product],
    age_years: int,
) -> Dict[str, Product]:
    return {
        code: p for code, p in catalog.items() if p.is_allowed_for_age(age_years)
    }


def recommend_stack_codes_for_goal(
    catalog: Dict[str, Product],
    age_profile: AgeProfile,
    age_years: int,
    goal: CosmeticGoal,
) -> List[str]:
    """
    Very simple, rule-based recommender that picks a few products
    based on the cosmetic goal and age.

    Later, this can be upgraded to a proper AI-planner hooked to StegVerse Core.
    """
    allowed = _filter_allowed_by_age(catalog, age_years)
    codes: List[str] = []

    # Helpers to add product if available + respects max_steps
    def add(code: str) -> None:
        if len(codes) >= goal.max_steps:
            return
        if code in allowed:
            codes.append(code)

    # --- Goal-specific heuristics ---

    if goal.goal_type == CosmeticGoalType.DAILY_MAINTENANCE:
        # daily: light polish, maybe mineral, light gloss
        add("C1")
        add("D1")
        add("E1")

    elif goal.goal_type == CosmeticGoalType.GENTLE_START:
        # gentle whitening start (teens/adults/seniors)
        add("A1")
        add("C1")
        add("D1")

    elif goal.goal_type == CosmeticGoalType.MINERAL_SUPPORT:
        # focus on minerals and surface comfort
        add("D1")
        add("C1")

    elif goal.goal_type == CosmeticGoalType.EVENT_MAXIMIZE:
        # event-day: push gloss + brightness, then overlays
        # adult stack: A2 + C2 + E1 + F1 (if available)
        if age_profile.group in (AgeGroup.ADULTS, AgeGroup.SENIORS):
            add("A2")
            add("C2")
            add("E1")
            add("F1")
        else:
            # For teens / kids, avoid high-intensity stack
            add("C2" if "C2" in allowed else "C1")
            add("E1")

    # Tone preference: if user wants "cool", favor F1; warm could map to F2 later
    if goal.tone_preference == "cool" and "F1" in allowed and "F1" not in codes:
        add("F1")

    # Deduplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            deduped.append(c)

    # Fall-back: if nothing is allowed, suggest at least C1 for anyone 5+
    if not deduped and "C1" in allowed:
        deduped.append("C1")

    return deduped
