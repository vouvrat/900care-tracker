from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.db import get_session
from app.services.consumption import compute_product_stats
from app.services.settings import get_or_create_settings
from app.services.suggestions import compute_order_suggestions
from app.templating import templates
from app.models import Member
from sqlmodel import select

router = APIRouter()


@router.get("/")
def dashboard(request: Request, session: Session = Depends(get_session)):
    settings = get_or_create_settings(session)
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    stats = compute_product_stats(session)
    suggestions = compute_order_suggestions(session, settings.order_coverage_months)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "members": members,
            "stats": stats,
            "suggestions": suggestions,
            "settings": settings,
        },
    )
