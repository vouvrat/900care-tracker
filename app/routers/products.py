from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import CatalogItem, CatalogSyncLog, Product
from app.services.catalog_sync import refresh_catalog_cache, seed_catalog_cache_if_empty
from app.templating import templates

router = APIRouter()


@router.get("/products")
def products_page(request: Request, session: Session = Depends(get_session)):
    seed_catalog_cache_if_empty(session)

    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    active_names = {p.name.strip().lower() for p in products}

    catalog_items = session.exec(select(CatalogItem).order_by(CatalogItem.name)).all()
    catalog_view = [
        {"item": c, "active": c.name.strip().lower() in active_names}
        for c in catalog_items
    ]

    last_sync = session.exec(
        select(CatalogSyncLog).order_by(CatalogSyncLog.ran_at.desc())
    ).first()
    return templates.TemplateResponse(
        request,
        "products.html",
        {"products": products, "catalog_view": catalog_view, "last_sync": last_sync},
    )


@router.post("/products/refresh-catalog")
def refresh_catalog(session: Session = Depends(get_session)):
    refresh_catalog_cache(session)
    return RedirectResponse("/products", status_code=303)


@router.post("/products/catalog/{catalog_item_id}/toggle")
def toggle_catalog_product(catalog_item_id: int, session: Session = Depends(get_session)):
    catalog_item = session.get(CatalogItem, catalog_item_id)
    if not catalog_item:
        return RedirectResponse("/products", status_code=303)

    existing = session.exec(
        select(Product).where(Product.name == catalog_item.name)
    ).first()

    if existing:
        existing.active = not existing.active
        session.add(existing)
    else:
        session.add(Product(
            name=catalog_item.name,
            category=catalog_item.category,
            unit="unité",
            image_url=catalog_item.image_url,
            active=True,
        ))
    session.commit()
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


@router.post("/products/{product_id}/update")
def update_product(
    product_id: int,
    category: str = Form(""),
    unit: str = Form("unité"),
    notes: str = Form(""),
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if product:
        product.category = category.strip()
        product.unit = unit.strip() or "unité"
        product.notes = notes.strip()
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
