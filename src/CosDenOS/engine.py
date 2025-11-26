from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .age import AgeProfile
from .catalog import build_default_catalog
from .errors import AgeGateError, UnknownProductError
from .goals import CosmeticGoal
from .models import Product, ProductEffect, ProductStack, SimulationResult
from .recommend import recommend_stack_codes_for_goal


class CosDenOS:
    """
    Core orchestration class for the CosDen cosmetic engine.

    Responsibilities:
    - Manage a catalog of cosmetic products (A→J series)
    - Enforce age-based gating rules per product
    - Combine product effects to simulate a cosmetic stack
    - Recommend product stacks for high-level cosmetic goals
    - Integrate with an external Digital Twin (just referenced here)
    """

    def __init__(self) -> None:
        self._catalog: Dict[str, Product] = {}
        self._devices: Dict[str, object] = {}
        self._twin: Optional[object] = None  # type: ignore[assignment]

    # -------------------------
    # Catalog management
    # -------------------------

    def load_default_catalog(self) -> None:
        self._catalog = build_default_catalog()

    def set_catalog(self, catalog: Dict[str, Product]) -> None:
        self._catalog = dict(catalog)

    def get_product(self, code: str) -> Product:
        try:
            return self._catalog[code]
        except KeyError as exc:
            raise UnknownProductError(f"Unknown product code: {code}") from exc

    def list_products(self) -> List[Product]:
        return list(self._catalog.values())

    # -------------------------
    # Devices
    # -------------------------

    def register_device(self, name: str, device_obj: object) -> None:
        self._devices[name] = device_obj

    def get_device(self, name: str) -> Optional[object]:
        return self._devices.get(name)

    # -------------------------
    # Digital Twin
    # -------------------------

    def load_twin(self, twin: object) -> None:
        """
        Attach an external Digital Twin object.

        CosDenOS does not interpret it medically; it is
        treated as a rendering/simulation target.
        """
        self._twin = twin

    @property
    def twin_loaded(self) -> bool:
        return self._twin is not None

    # -------------------------
    # Stack helpers
    # -------------------------

    def build_stack(self, codes: Iterable[str]) -> ProductStack:
        products: List[Product] = [self.get_product(code) for code in codes]
        return ProductStack(products=products)

    # -------------------------
    # Simulation
    # -------------------------

    def simulate_stack(
        self,
        stack: ProductStack,
        age_profile: AgeProfile,
        age_years: int,
    ) -> SimulationResult:
        """
        Simulate a purely cosmetic effect of a product stack.

        - Checks age gating for each product.
        - Aggregates ProductEffect for all products in order.
        - Returns a SimulationResult with human-readable notes.
        """
        aggregated = ProductEffect()
        notes: List[str] = []

        for product in stack.products:
            if not product.is_allowed_for_age(age_years):
                raise AgeGateError(
                    f"Product {product.code} is not allowed for age {age_years}."
                )

            aggregated = aggregated.merge(product.effect)
            notes.append(
                f"{product.code}: {product.name} → "
                f"Δbrightness={product.effect.brightness_delta:+.2f}, "
                f"Δgloss={product.effect.gloss_delta:+.2f}, "
                f"Δopal={product.effect.opalescence_delta:+.2f}, "
                f"tone={product.effect.tone_shift or 'unchanged'}"
            )

        if self._twin is None:
            notes.append("No Digital Twin loaded: visualization-only preview.")
        else:
            notes.append("Digital Twin loaded: effects can be mapped to a 3D model.")

        notes.append(
            f"Age profile: {age_profile.group.value} "
            f"(cosmetic guidance only, no diagnosis)."
        )

        return SimulationResult(
            stack_codes=stack.codes(),
            aggregated_effect=aggregated,
            notes=notes,
            cosmetic_only=True,
        )

    # -------------------------
    # Recommendation
    # -------------------------

    def recommend_stack_for_goal(
        self,
        age_profile: AgeProfile,
        age_years: int,
        goal: CosmeticGoal,
    ) -> ProductStack:
        """
        High-level intention → recommended product stack.

        Uses a simple rule-based planner under the hood (for now).
        """
        codes = recommend_stack_codes_for_goal(
            catalog=self._catalog,
            age_profile=age_profile,
            age_years=age_years,
            goal=goal,
        )
        return self.build_stack(codes)
