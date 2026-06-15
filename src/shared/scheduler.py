import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
_scheduler = BackgroundScheduler()


def _expire_pending_appointments() -> None:
    from shared.db import db_session
    from repositories.appointment_repository import AppointmentRepository

    try:
        with db_session() as db:
            threshold = datetime.now(timezone.utc) - timedelta(minutes=15)
            count = AppointmentRepository.expire_old_pending(db, threshold)
            if count:
                logger.info("Expiration automatique : %d rendez-vous passés en expired", count)
    except Exception:
        logger.exception("Erreur lors de l'expiration des RDV")


def start_scheduler() -> None:
    _scheduler.add_job(_expire_pending_appointments, "interval", minutes=5)
    _scheduler.start()
    logger.info("Scheduler démarré.")


def stop_scheduler() -> None:
    _scheduler.shutdown(wait=False)
    logger.info("Scheduler arrêté.")
