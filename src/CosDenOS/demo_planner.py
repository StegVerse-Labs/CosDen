from CosDenOS import CosDenOS
from CosDenOS.ai_planner import CosmeticPlannerAgent
from CosDenOS.user_profile import CosmeticUserProfile

engine = CosDenOS()
engine.load_default_catalog()

user = CosmeticUserProfile.from_age(
    age_years=35,
    tone_preference="cool",
    sensitivity_flag=True,
    event_time_hours=24,
    notes="Coffee drinker, wants gentle whitening before event."
)

agent = CosmeticPlannerAgent(engine=engine, llm_client=None)

plan = agent.plan_for_request(
    user=user,
    request_text="Gentle cosmetic whitening and gloss for an important event tomorrow.",
)

# 'plan' is a dict ready to JSONify / send back over an API
print(plan)
