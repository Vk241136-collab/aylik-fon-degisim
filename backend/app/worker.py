import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings
from app.services.kap_sync import KapSyncService


async def main() -> None:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    service = KapSyncService()
    scheduler.add_job(service.run_once, "interval", minutes=settings.kap_poll_interval_minutes, id="kap-sync", max_instances=1)
    scheduler.start()
    await service.run_once()
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
