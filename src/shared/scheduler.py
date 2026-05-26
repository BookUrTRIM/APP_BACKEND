import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
_scheduler = BackgroundScheduler()


def _expire_pending_appointments() -> None:
    from repositories.appointment_repository import AppointmentRepository
    threshold = datetime.now(timezone.utc) - timedelta(minutes=15)
    count = AppointmentRepository.expire_old_pending(threshold)
    if count:
        logger.info("Expiration automatique : %d rendez-vous passés en expired", count)


def start_scheduler() -> None:
    _scheduler.add_job(_expire_pending_appointments, "interval", minutes=5)
    _scheduler.start()
    logger.info("Scheduler démarré.")


def stop_scheduler() -> None:
    _scheduler.shutdown(wait=False)
    logger.info("Scheduler arrêté.")
