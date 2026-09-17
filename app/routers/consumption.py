from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import ConsumptionEvent, Member, Product
from app.templating import templates

router = APIRouter()


@router.get("/log")
def log_page(request: Request, session: Session = Depends(get_session)):
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    products = session.exec(
        select(Product).where(Product.active == True).order_by(Product.name)  # noqa: E712
    ).all()
    recent_events = session.exec(
        select(ConsumptionEvent).order_by(ConsumptionEvent.id.desc()).limit(20)
    ).all()
    members_by_id = {m.id: m for m in members}
    products_by_id = {p.id: p for p in products}
    return templates.TemplateResponse(
        request,
        "log.html",
        {
            "members": members,
            "products": products,
            "recent_events": recent_events,
            "members_by_id": members_by_id,
            "products_by_id": products_by_id,
        },
    )


@router.post("/log")
def create_event(
    member_id: int = Form(...),
    product_id: int = Form(...),
    event_type: str = Form(...),
    quantity: float = Form(1.0),
    event_date: date = Form(default_factory=date.today),
    session: Session = Depends(get_session),
):
    if event_type not in ("started", "finished"):
        event_type = "started"
    event = ConsumptionEvent(
        member_id=member_id,
        product_id=product_id,
        event_type=event_type,
        quantity=quantity,
        event_date=event_date,
    )
    session.add(event)
    session.commit()
    return RedirectResponse("/log", status_code=303)


@router.post("/log/{event_id}/delete")
def delete_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(ConsumptionEvent, event_id)
    if event:
        session.delete(event)
        session.commit()
    return RedirectResponse("/log", status_code=303)
