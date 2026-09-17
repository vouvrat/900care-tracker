from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.catalog_900care import CATALOG_900CARE
from app.db import get_session
from app.models import CatalogSyncLog, Product
from app.services.catalog_sync import sync_catalog
from app.templating import templates

router = APIRouter()


@router.get("/products")
def products_page(request: Request, session: Session = Depends(get_session)):
    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    existing_names = {p.name.strip().lower() for p in products}
    catalog_remaining = [c for c in CATALOG_900CARE if c["name"].strip().lower() not in existing_names]
    last_sync = session.exec(
        select(CatalogSyncLog).order_by(CatalogSyncLog.ran_at.desc())
    ).first()
    return templates.TemplateResponse(
        request,
        "products.html",
        {"products": products, "catalog_remaining": catalog_remaining, "last_sync": last_sync},
    )


@router.post("/products/import-catalog")
def import_catalog(session: Session = Depends(get_session)):
    sync_catalog(session)
    return RedirectResponse("/products", status_code=303)


@router.post("/products")
def create_product(
    name: str = Form(...),
    category: str = Form(""),
    unit: str = Form("unité"),
    notes: str = Form(""),
    session: Session = Depends(get_session),
):
    product = Product(
        name=name.strip(),
        category=category.strip(),
        unit=unit.strip() or "unité",
        notes=notes.strip(),
    )
    session.add(product)
    session.commit()
    return RedirectResponse("/products", status_code=303)


@router.post("/products/{product_id}/delete")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product:
        product.active = False
        session.add(product)
        session.commit()
    return RedirectResponse("/products", status_code=303)
