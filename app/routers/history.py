from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from app.db import get_session
from app.models import ConsumptionEvent, Member, Product, Review
from app.templating import templates

router = APIRouter()


@router.get("/history")
def history_page(
    request: Request,
    member_id: str = "",
    product_id: str = "",
    session: Session = Depends(get_session),
):
    member_id = int(member_id) if member_id.strip() else None
    product_id = int(product_id) if product_id.strip() else None
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    members_by_id = {m.id: m for m in members}
    products_by_id = {p.id: p for p in products}

    events_query = select(ConsumptionEvent)
    reviews_query = select(Review)
    if member_id:
        events_query = events_query.where(ConsumptionEvent.member_id == member_id)
        reviews_query = reviews_query.where(Review.member_id == member_id)
    if product_id:
        events_query = events_query.where(ConsumptionEvent.product_id == product_id)
        reviews_query = reviews_query.where(Review.product_id == product_id)

    events = session.exec(events_query).all()
    reviews = session.exec(reviews_query).all()

    timeline = []
    for e in events:
        timeline.append(
            {
                "date": e.event_date,
                "kind": "conso",
                "label": f"{members_by_id.get(e.member_id).name if members_by_id.get(e.member_id) else '?'} — {products_by_id.get(e.product_id).name if products_by_id.get(e.product_id) else '?'} ({e.event_type})",
            }
        )
    for r in reviews:
        member_name = members_by_id.get(r.member_id).name if r.member_id and members_by_id.get(r.member_id) else "Foyer"
        timeline.append(
            {
                "date": r.review_date,
                "kind": "avis",
                "label": f"{member_name} — {products_by_id.get(r.product_id).name if products_by_id.get(r.product_id) else '?'} : {r.rating}/5 {r.comment}",
            }
        )
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return templates.TemplateResponse(
        request,
        "history.html",
        {
            "members": members,
            "products": products,
            "timeline": timeline,
            "selected_member_id": member_id,
            "selected_product_id": product_id,
        },
    )
