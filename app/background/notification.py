import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User
from app.services.EMAIL_SERVICE.notification_service import NotificationService

logger = logging.getLogger(__name__)
notification = NotificationService()


async def send_event_reminders() -> None:
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(hours=24)
    window_end   = now + timedelta(hours=25)   # 1-hour window for hourly runs

    logger.info(
        "Reminder job started — looking for events between %s and %s",
        window_start.isoformat(), window_end.isoformat(),
    )

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Registration)
            .join(Registration.event)
            .join(Registration.user)
            .where(
                Event.start_time >= window_start,
                Event.start_time <  window_end,
                Registration.status != "cancelled",
                User.is_active == 1,
            )
            .options(
                selectinload(Registration.event),
                selectinload(Registration.user),
            )
        )
        registrations = result.scalars().all()

    if not registrations:
        logger.info("No upcoming events in window — nothing to send.")
        return

    logger.info("Found %d registration(s) to notify.", len(registrations))

    ok = fail = 0
    for reg in registrations:
        user  = reg.user
        event = reg.event
        try:
            await notification.send_event_reminder(
                recipient_email=user.email,
                user_name=user.username,
                event_name=event.title,
                event_start=event.start_time,
                event_location=event.location,
            )
            logger.info(
                "Reminder sent → %s for event '%s'", user.email, event.title
            )
            ok += 1
        except Exception as exc:
            logger.error(
                "Failed to send reminder to %s for event '%s': %s",
                user.email, event.title, exc,
            )
            fail += 1

    logger.info("Reminder job done — sent: %d, failed: %d", ok, fail)


def start_scheduler() -> None:

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError:
        logger.warning(
            "APScheduler not installed — scheduler not started. "
            "Install it with: pip install apscheduler"
        )
        return

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_event_reminders,
        trigger="interval",
        hours=1,
        id="event_reminder",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    logger.info("APScheduler started — reminder job runs every hour.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )
    asyncio.run(send_event_reminders())