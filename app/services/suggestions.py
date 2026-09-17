import math
from dataclasses import dataclass

from sqlmodel import Session

from app.services.consumption import ProductStats, compute_product_stats


@dataclass
class OrderSuggestion:
    product_name: str
    unit: str
    household_monthly_rate: float
    suggested_quantity: int


def compute_order_suggestions(
    session: Session, coverage_months: float
) -> list[OrderSuggestion]:
    stats: list[ProductStats] = compute_product_stats(session)
    suggestions = []
    for s in stats:
        if s.household_monthly_rate <= 0:
            continue
        qty = math.ceil(s.household_monthly_rate * coverage_months)
        suggestions.append(
            OrderSuggestion(
                product_name=s.product.name,
                unit=s.product.unit,
                household_monthly_rate=s.household_monthly_rate,
                suggested_quantity=qty,
            )
        )
    return sorted(suggestions, key=lambda x: -x.suggested_quantity)
