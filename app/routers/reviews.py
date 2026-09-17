from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Member, Product, Review
from app.templating import templates

router = APIRouter()


@router.get("/reviews")
def reviews_page(request: Request, session: Session = Depends(get_session)):
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    reviews = session.exec(select(Review).order_by(Review.id.desc())).all()
    members_by_id = {m.id: m for m in members}
    products_by_id = {p.id: p for p in products}
    return templates.TemplateResponse(
        request,
        "reviews.html",
        {
            "members": members,
            "products": products,
            "reviews": reviews,
            "members_by_id": members_by_id,
            "products_by_id": products_by_id,
        },
    )


@router.post("/reviews")
def create_review(
    product_id: int = Form(...),
    member_id: str = Form(""),
    rating: int = Form(...),
    comment: str = Form(""),
    review_date: date = Form(default_factory=date.today),
    session: Session = Depends(get_session),
):
    rating = min(5, max(1, rating))
    review = Review(
        product_id=product_id,
        member_id=int(member_id) if member_id.strip() else None,
        rating=rating,
        comment=comment.strip(),
        review_date=review_date,
    )
    session.add(review)
    session.commit()
    return RedirectResponse("/reviews", status_code=303)
