"""Tâche planifiée : synchronise le catalogue 900 Care chaque semaine."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session

from app.db import engine
from app.services.catalog_sync import sync_catalog

logger = logging.getLogger("uvicorn.error")

_scheduler = BackgroundScheduler(timezone="Europe/Paris")


def _run_sync_job() -> None:
    with Session(engine) as session:
        log = sync_catalog(session)
        if log.error:
            logger.warning("Sync catalogue 900 Care en repli (%s) : %s", log.source, log.error)
        else:
            logger.info("Sync catalogue 900 Care OK : %s produit(s) ajouté(s)", log.added_count)


def start_scheduler() -> None:
    if _scheduler.running:
        return
    # Chaque dimanche à 4h du matin — trafic faible côté 900.care, NAS généralement allumé.
    _scheduler.add_job(_run_sync_job, CronTrigger(day_of_week="sun", hour=4, minute=0), id="catalog_sync_weekly")
    _scheduler.start()
