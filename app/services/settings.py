from sqlmodel import Session, select

from app.models import HouseholdSettings, Member


def get_or_create_settings(session: Session) -> HouseholdSettings:
    settings = session.exec(select(HouseholdSettings)).first()
    if settings is None:
        settings = HouseholdSettings()
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings


def sync_member_count(session: Session, target_size: int) -> None:
    """Ajuste le nombre de membres actifs pour correspondre à la taille du foyer.

    Ajoute des membres 'Membre N' si besoin, désactive les excédentaires
    (sans supprimer l'historique de conso/avis qui leur est associé).
    """
    members = session.exec(
        select(Member).where(Member.active == True).order_by(Member.id)  # noqa: E712
    ).all()
    current = len(members)

    if target_size > current:
        for i in range(current + 1, target_size + 1):
            session.add(Member(name=f"Membre {i}"))
    elif target_size < current:
        for member in members[target_size:]:
            member.active = False
            session.add(member)

    session.commit()
