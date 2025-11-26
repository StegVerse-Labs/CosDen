from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
import json


class ProductSeries(str, Enum):
    A = "A"  # Whitening gels
    B = "B"  # Resin infiltrants
    C = "C"  # Daily polish
    D = "D"  # Mineral trays
    E = "E"  # Overlay films
    F = "F"  # Event boosters
    G = "G"  # Tone tuners
    H = "H"  # Opal tuners
    I = "I"  # Protective coatings
    J = "J"  # Cosmetic veneer films


@dataclass
class ProductEffect:
    """
    High-level cosmetic-only effect description.

    We avoid any medical metrics (no 'damage', 'sensitivity scores', etc.).
    """
    brightness_delta: float = 0.0    # + = brighter, - = dimmer
    gloss_delta: float = 0.0         # perceived gloss change
    tone_shift: Optional[str] = None # "cool", "warm", "neutral"
    opalescence_delta: float = 0.0   # perceived depth of "pearl" look

    def merge(self, other: "ProductEffect") -> "ProductEffect":
        """
        Combine two effects; tone_shift is overwritten by 'other' if present.
        """
        tone = other.tone_shift or self.tone_shift
        return ProductEffect(
            brightness_delta=self.brightness_delta + other.brightness_delta,
            gloss_delta=self.gloss_delta + other.gloss_delta,
            tone_shift=tone,
            opalescence_delta=self.opalescence_delta + other.opalescence_delta,
        )


@dataclass
class Product:
    code: str                      # e.g. "A1", "C2", "E1"
    name: str                      # e.g. "BrightCore"
    series: ProductSeries          # A–J
    description: str               # human-readable description
    effect: ProductEffect          # cosmetic effect profile
    age_min: int = 13              # min age recommended
    age_max: Optional[int] = None  # None = no upper bound
    intensity_level: int = 1       # 1–3 rough intensity

    def is_allowed_for_age(self, age_years: int) -> bool:
        if age_years < self.age_min:
            return False
        if self.age_max is not None and age_years > self.age_max:
            return False
        return True


@dataclass
class ProductStack:
    """
    A set of products applied in a particular order for simulation.
    """
    products: List[Product]

    def codes(self) -> List[str]:
        return [p.code for p in self.products]


@dataclass
class SimulationResult:
    """
    Result of a cosmetic-only simulation for a given Digital Twin + stack.
    """
    stack_codes: List[str]
    aggregated_effect: ProductEffect
    notes: List[str] = field(default_factory=list)
    cosmetic_only: bool = True

    def describe(self) -> str:
        tone = self.aggregated_effect.tone_shift or "no tone shift"
        return (
            f"Stack: {', '.join(self.stack_codes)}\n"
            f"- Brightness delta: {self.aggregated_effect.brightness_delta:+.2f}\n"
            f"- Gloss delta: {self.aggregated_effect.gloss_delta:+.2f}\n"
            f"- Opalescence delta: {self.aggregated_effect.opalescence_delta:+.2f}\n"
            f"- Tone shift: {tone}\n"
            f"Notes:\n  - " + "\n  - ".join(self.notes or ["No additional notes."]) +
            "\n(This is a cosmetic-only simulation, not a diagnosis or treatment.)"
        )

    def to_dict(self) -> Dict:
        """
        Convert to a plain dict (JSON-safe).
        """
        base = asdict(self)
        # Enum-safe conversion inside nested structures
        base["aggregated_effect"]["tone_shift"] = self.aggregated_effect.tone_shift
        return base

    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        JSON representation of the simulation result, for APIs / logs.
        """
        return json.dumps(self.to_dict(), indent=indent)
