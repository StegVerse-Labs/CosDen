from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from .age import AgeProfile, AgeGroup
from .engine import CosDenOS
from .goals import CosmeticGoal, CosmeticGoalType
from .llm_client import LLMClient
from .models import ProductStack, SimulationResult
from .user_profile import CosmeticUserProfile


class CosmeticPlannerAgent:
    """
    StegVerse AI Cosmetic Planner for CosDen.

    Responsibilities:
    - Interpret a user's cosmetic intent (natural language) into a CosmeticGoal
    - Ask CosDenOS for a recommended product stack
    - Simulate the cosmetic effect on the user's Digital Twin (if present)
    - Return a structured, cosmetic-only plan

    This agent is designed so that:
    - It can run in a purely rule-based mode (no LLM).
    - It can later use an LLMClient to refine understanding of user intent.
    """

    def __init__(
        self,
        engine: CosDenOS,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        self.engine = engine
        self.llm_client = llm_client

    # -----------------------------
    # Public entry point
    # -----------------------------

    def plan_for_request(
        self,
        user: CosmeticUserProfile,
        request_text: str,
    ) -> Dict[str, Any]:
        """
        Main entry-point for StegVerse-AI.

        Inputs:
          - user: CosmeticUserProfile
          - request_text: free-text description of the cosmetic goal

        Output:
          - structured dict describing:
              - interpreted goal
              - recommended product codes
              - simulation summary
        """
        # 1) Interpret textual intent → CosmeticGoal
        goal = self._interpret_goal(user, request_text)

        # 2) Ask CosDenOS for the recommended stack for that goal
        stack = self.engine.recommend_stack_for_goal(
            age_profile=user.age_profile,
            age_years=user.age_years,
            goal=goal,
        )

        # 3) Simulate the stack's cosmetic effect
        sim_result = self.engine.simulate_stack(
            stack=stack,
            age_profile=user.age_profile,
            age_years=user.age_years,
        )

        # 4) Package into a structured response
        return self._build_plan_response(
            user=user,
            goal=goal,
            stack=stack,
            sim_result=sim_result,
            raw_request=request_text,
        )

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _interpret_goal(
        self,
        user: CosmeticUserProfile,
        request_text: str,
    ) -> CosmeticGoal:
        """
        Very simple text → goal mapping for now.

        Later, this can:
          - Call self.llm_client.complete(prompt=...) to get richer intent
          - Use that to choose more nuanced stacks
        """
        text = request_text.lower()

        # Choose a base goal_type
        if any(k in text for k in ["wedding", "photoshoot", "photo shoot", "big event", "red carpet", "tonight", "tomorrow"]):
            goal_type = CosmeticGoalType.EVENT_MAXIMIZE
        elif any(k in text for k in ["every day", "daily", "routine", "maintenance"]):
            goal_type = CosmeticGoalType.DAILY_MAINTENANCE
        elif any(k in text for k in ["gentle", "sensitive", "start", "first time"]):
            goal_type = CosmeticGoalType.GENTLE_START
        elif any(k in text for k in ["mineral", "comfort", "tray", "overnight"]):
            goal_type = CosmeticGoalType.MINERAL_SUPPORT
        else:
            # Default heuristic: kids/teens → gentle, adults/seniors → daily
            if user.age_profile.group in (AgeGroup.KIDS, AgeGroup.TEENS) or user.sensitivity_flag:
                goal_type = CosmeticGoalType.GENTLE_START
            else:
                goal_type = CosmeticGoalType.DAILY_MAINTENANCE

        # Tone preference override from text (if not already set in profile)
        tone = user.tone_preference
        if tone is None:
            if "cool" in text or "blue white" in text:
                tone = "cool"
            elif "warm" in text or "golden" in text:
                tone = "warm"
            elif "neutral" in text or "porcelain" in text:
                tone = "neutral"

        # Event time hint from text, if not already set
        event_hours = user.event_time_hours
        if event_hours is None and goal_type == CosmeticGoalType.EVENT_MAXIMIZE:
            if "tonight" in text:
                event_hours = 8
            elif "tomorrow" in text or "24 hours" in text:
                event_hours = 24

        # Sensitivity → prefer fewer steps
        max_steps = 3 if user.sensitivity_flag else 4

        return CosmeticGoal(
            goal_type=goal_type,
            tone_preference=tone,
            max_steps=max_steps,
            target_event_hours=event_hours,
        )

    def _build_plan_response(
        self,
        user: CosmeticUserProfile,
        goal: CosmeticGoal,
        stack: ProductStack,
        sim_result: SimulationResult,
        raw_request: str,
    ) -> Dict[str, Any]:
        """
        Build a JSON-friendly plan object for use by other StegVerse pieces.
        """
        return {
            "version": "1.0",
            "cosmetic_only": True,
            "raw_request": raw_request,
            "user": {
                "age_years": user.age_years,
                "age_group": user.age_profile.group.value,
                "tone_preference": user.tone_preference,
                "sensitivity_flag": user.sensitivity_flag,
                "event_time_hours": user.event_time_hours,
                "notes": user.notes,
            },
            "interpreted_goal": {
                "goal_type": goal.goal_type.value,
                "tone_preference": goal.tone_preference,
                "max_steps": goal.max_steps,
                "target_event_hours": goal.target_event_hours,
            },
            "recommended_stack": {
                "codes": stack.codes(),
                "products": [
                    {
                        "code": p.code,
                        "name": p.name,
                        "series": p.series.value,
                        "intensity_level": p.intensity_level,
                        "description": p.description,
                    }
                    for p in stack.products
                ],
            },
            "simulation": sim_result.to_dict(),
            "legal_disclaimer": (
                "This plan is cosmetic-only. It does not diagnose, treat, "
                "or prevent any disease or condition. For medical or dental "
                "questions, consult a licensed professional."
            ),
        }
