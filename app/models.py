from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HouseholdSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    household_size: int = 4
    order_coverage_months: float = 2.0


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str = ""
    unit: str = "unité"
    notes: str = ""
    active: bool = True
    image_url: str = ""


class ConsumptionEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    member_id: int = Field(foreign_key="member.id")
    event_type: str  # "started" | "finished"
    quantity: float = 1.0
    event_date: date = Field(default_factory=date.today)


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    member_id: Optional[int] = Field(default=None, foreign_key="member.id")
    rating: int
    comment: str = ""
    review_date: date = Field(default_factory=date.today)


class CatalogSyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    source: str  # "live" | "fallback"
    added_count: int = 0
    error: str = ""


class CatalogItem(SQLModel, table=True):
    """Catalogue connu de 900 Care (cache local, rafraîchi chaque semaine).

    Ne représente pas un produit suivi : c'est la liste de référence dans
    laquelle l'utilisateur active/désactive un produit au cas par cas.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    category: str = ""
    image_url: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)
