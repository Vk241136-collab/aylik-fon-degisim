from __future__ import annotations

from datetime import datetime

import httpx

from app.core.config import get_settings
from app.domain.kap import KapDisclosureRecord, KapFundRecord


class KapClient:
    """Small, respectful KAP access adapter.

    KAP integration must stay configurable because public page structures and any
    official data-access terms can change. Production should prefer an approved
    data feed or documented endpoint when available.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.kap_base_url.rstrip("/")
        self.timeout = settings.kap_request_timeout_seconds
        self.headers = {"User-Agent": settings.kap_user_agent}

    async def fetch_fund_catalog(self) -> list[KapFundRecord]:
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}/tr")
            response.raise_for_status()
            html = response.text

        # The first production connector should be replaced with a documented KAP
        # feed when one is contracted or published. This fallback only proves the
        # pipeline and keeps network access centralized.
        if "Fonlar" not in html:
            return []
        return []

    async def fetch_recent_fund_disclosures(self, since: datetime | None = None) -> list[KapDisclosureRecord]:
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            response = await client.get(f"{self.base_url}/tr")
            response.raise_for_status()
            html = response.text

        if "Fon Bildirimleri" not in html:
            return []
        return []
