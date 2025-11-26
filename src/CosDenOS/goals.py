from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CosmeticGoalType(str, Enum):
    DAILY_MAINTENANCE = "daily_maintenance"
    EVENT_MAXIMIZE = "event_maximize"
    GENTLE_START = "gentle_start"
    MINERAL_SUPPORT = "mineral_support"


@dataclass
class CosmeticGoal:
    """
    High-level cosmetic intent from the user.

    Examples:
      - "daily maintenance"
      - "big event tonight"
      - "start whitening gently"
      - "focus on minerals & comfort"
    """
    goal_type: CosmeticGoalType
    tone_preference: Optional[str] = None  # "cool", "warm", "neutral", or None
    max_steps: int = 4
    target_event_hours: Optional[int] = None  # e.g. 24 for 'tomorrow'
