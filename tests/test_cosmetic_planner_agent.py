from CosDenOS import CosDenOS
from CosDenOS.ai_planner import CosmeticPlannerAgent
from CosDenOS.user_profile import CosmeticUserProfile


def test_planner_builds_cosmetic_plan_for_event():
    engine = CosDenOS()
    engine.load_default_catalog()

    user = CosmeticUserProfile.from_age(
        age_years=32,
        tone_preference=None,
        sensitivity_flag=False,
        event_time_hours=None,
        notes="Photoshoot tomorrow, wants cool white."
    )

    agent = CosmeticPlannerAgent(engine=engine, llm_client=None)

    plan = agent.plan_for_request(
        user=user,
        request_text="I have a big photoshoot tomorrow and want a cool white smile, but still within safe cosmetic ranges.",
    )

    assert plan["cosmetic_only"] is True
    assert plan["interpreted_goal"]["goal_type"] == "event_maximize"
    assert plan["user"]["age_group"] == "adults"
    assert len(plan["recommended_stack"]["codes"]) >= 1

    sim = plan["simulation"]
    assert sim["cosmetic_only"] is True
    assert sim["aggregated_effect"]["brightness_delta"] > 0.0
