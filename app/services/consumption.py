from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from sqlmodel import Session, select

from app.models import ConsumptionEvent, Member, Product


@dataclass
class CellStats:
    finished_count: int
    last_event_date: Optional[str]
    monthly_rate: Optional[float]  # unités/mois pour ce membre sur ce produit


@dataclass
class ProductStats:
    product: Product
    per_member: dict  # member_id -> CellStats
    household_monthly_rate: float


def _monthly_rate_from_dates(dates: list) -> Optional[float]:
    """Rythme mensuel à partir des dates d'événements 'finished' triées."""
    if len(dates) < 2:
        return None
    dates = sorted(dates)
    intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
    avg_interval = sum(intervals) / len(intervals)
    if avg_interval <= 0:
        return None
    return 30.0 / avg_interval


def compute_product_stats(session: Session) -> list[ProductStats]:
    products = session.exec(select(Product).where(Product.active == True)).all()  # noqa: E712
    members = session.exec(select(Member).where(Member.active == True)).all()  # noqa: E712
    events = session.exec(select(ConsumptionEvent)).all()

    events_by_product_member = defaultdict(list)
    for e in events:
        if e.event_type == "finished":
            events_by_product_member[(e.product_id, e.member_id)].append(e.event_date)

    last_event_by_product_member = defaultdict(list)
    for e in events:
        last_event_by_product_member[(e.product_id, e.member_id)].append(e.event_date)

    stats = []
    for product in products:
        per_member = {}
        household_rate = 0.0
        for member in members:
            key = (product.id, member.id)
            finished_dates = events_by_product_member.get(key, [])
            all_dates = last_event_by_product_member.get(key, [])
            rate = _monthly_rate_from_dates(finished_dates)
            if rate:
                household_rate += rate
            per_member[member.id] = CellStats(
                finished_count=len(finished_dates),
                last_event_date=max(all_dates).isoformat() if all_dates else None,
                monthly_rate=round(rate, 2) if rate else None,
            )
        stats.append(
            ProductStats(
                product=product,
                per_member=per_member,
                household_monthly_rate=round(household_rate, 2),
            )
        )
    return stats
