import json

from CosDenOS import CosDenOS
from CosDenOS.age import AgeProfile
from CosDenOS.goals import CosmeticGoal, CosmeticGoalType


def test_recommend_and_simulate_event_for_adult():
    os_ = CosDenOS()
    os_.load_default_catalog()

    age_years = 30
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

    assert len(stack.products) >= 1
    codes = stack.codes()
    # We expect at least something like A2/C2/E1/F1 for adults if available
    assert any(code.startswith("A") for code in codes) or "E1" in codes

    result = os_.simulate_stack(
        stack=stack,
        age_profile=age_profile,
        age_years=age_years,
    )

    assert result.cosmetic_only is True
    assert result.aggregated_effect.brightness_delta > 0.0

    # JSON round trip
    s = result.to_json()
    data = json.loads(s)
    assert "stack_codes" in data
    assert isinstance(data["stack_codes"], list)


def test_kid_goal_never_returns_A_series():
    os_ = CosDenOS()
    os_.load_default_catalog()

    age_years = 10
    age_profile = AgeProfile.from_age(age_years)
    goal = CosmeticGoal(
        goal_type=CosmeticGoalType.EVENT_MAXIMIZE,
        max_steps=3,
    )

    stack = os_.recommend_stack_for_goal(
        age_profile=age_profile,
        age_years=age_years,
        goal=goal,
    )

    codes = stack.codes()
    # Kids should not get A-series whitening
    assert all(not c.startswith("A") for c in codes)
