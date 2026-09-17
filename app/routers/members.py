from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.db import get_session
from app.models import Member
from app.services.settings import get_or_create_settings, sync_member_count
from app.templating import templates

router = APIRouter()


@router.get("/members")
def members_page(request: Request, session: Session = Depends(get_session)):
    settings = get_or_create_settings(session)
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    return templates.TemplateResponse(
        request,
        "members.html",
        {"members": members, "settings": settings},
    )


@router.post("/members/household-size")
def set_household_size(
    household_size: int = Form(...), session: Session = Depends(get_session)
):
    settings = get_or_create_settings(session)
    household_size = max(1, household_size)
    settings.household_size = household_size
    session.add(settings)
    session.commit()
    sync_member_count(session, household_size)
    return RedirectResponse("/members", status_code=303)


@router.post("/members/coverage")
def set_coverage(
    order_coverage_months: float = Form(...), session: Session = Depends(get_session)
):
    settings = get_or_create_settings(session)
    settings.order_coverage_months = max(0.5, order_coverage_months)
    session.add(settings)
    session.commit()
    return RedirectResponse("/members", status_code=303)


@router.post("/members/{member_id}/rename")
def rename_member(
    member_id: int, name: str = Form(...), session: Session = Depends(get_session)
):
    member = session.get(Member, member_id)
    if member:
        member.name = name.strip() or member.name
        session.add(member)
        session.commit()
    return RedirectResponse("/members", status_code=303)
