"""
Tiny demo of CosDenOS usage.

Run this on a dev machine with:

    python -m CosDenOS.demo

(Not required for GitHub Actions; just for humans.)
"""

from . import CosDenOS
from .age import AgeProfile
from .goals import CosmeticGoal, CosmeticGoalType


def main() -> None:
    os_ = CosDenOS()
    os_.load_default_catalog()

    # Example adult profile
    age_years = 35
    age_profile = AgeProfile.from_age(age_years)

    goal = CosmeticGoal(
        goal_type=CosmeticGoalType.EVENT_MAXIMIZE,
        tone_preference="cool",
        max_steps=4,
        target_event_hours=24,
    )

    stack = os_.recommend_stack_for_goal(
        age_profile=age_profile,
        age_years=age_years,
        goal=goal,
    )

    result = os_.simulate_stack(
        stack=stack,
        age_profile=age_profile,
        age_years=age_years,
    )

    print(result.describe())
    print("\nJSON:\n", result.to_json())


if __name__ == "__main__":
    main()
