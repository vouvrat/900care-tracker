from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Product
from app.templating import templates

router = APIRouter()


@router.get("/products")
def products_page(request: Request, session: Session = Depends(get_session)):
    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    return templates.TemplateResponse(
        request, "products.html", {"products": products}
    )


@router.post("/products")
def create_product(
    name: str = Form(...),
    category: str = Form(""),
    unit: str = Form("unité"),
    notes: str = Form(""),
    session: Session = Depends(get_session),
):
    product = Product(name=name.strip(), category=category.strip(), unit=unit.strip() or "unité", notes=notes.strip())
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
