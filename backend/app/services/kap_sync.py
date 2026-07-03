from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.config import get_settings
from app.domain.kap import KapSyncState
from app.domain.models import Fund, PortfolioManagementCompany
from app.services.kap_client import KapClient
from app.services.seed_data import companies, funds

kap_sync_state = KapSyncState(enabled=get_settings().kap_sync_enabled)


class KapSyncService:
    def __init__(self, client: KapClient | None = None) -> None:
        self.client = client or KapClient()

    async def run_once(self) -> KapSyncState:
        settings = get_settings()
        kap_sync_state.enabled = settings.kap_sync_enabled
        kap_sync_state.last_started_at = datetime.utcnow()
        kap_sync_state.last_status = "RUNNING"
        kap_sync_state.errors.clear()

        if not settings.kap_sync_enabled:
            kap_sync_state.last_status = "DISABLED"
            kap_sync_state.last_message = "KAP senkronizasyonu kapalı. KAP_SYNC_ENABLED=true yapılınca çalışır."
            kap_sync_state.last_finished_at = datetime.utcnow()
            return kap_sync_state

        try:
            catalog = await self.client.fetch_fund_catalog()
            disclosures = await self.client.fetch_recent_fund_disclosures()
            imported = self._upsert_catalog(catalog)
            kap_sync_state.discovered_funds = imported
            kap_sync_state.discovered_disclosures = len(disclosures)
            kap_sync_state.downloaded_reports = 0
            kap_sync_state.parse_jobs_created = 0
            kap_sync_state.last_status = "SUCCESS"
            kap_sync_state.last_message = "KAP kontrolü tamamlandı."
        except Exception as exc:  # noqa: BLE001
            kap_sync_state.last_status = "FAILED"
            kap_sync_state.last_message = "KAP senkronizasyonu tamamlanamadı."
            kap_sync_state.errors.append(str(exc))
        finally:
            kap_sync_state.last_finished_at = datetime.utcnow()

        return kap_sync_state

    def _upsert_catalog(self, catalog) -> int:
        imported = 0
        for item in catalog:
            if not item.code or not item.name:
                continue
            company_name = item.company_name or "Bilinmeyen Portföy"
            company = next((row for row in companies.values() if row.name == company_name), None)
            if company is None:
                company = PortfolioManagementCompany(name=company_name, id=uuid4())
                companies[company.id] = company
            existing = next((row for row in funds.values() if row.code == item.code), None)
            if existing is None:
                fund = Fund(code=item.code, name=item.name, company_id=company.id)
                funds[fund.id] = fund
            else:
                existing.name = item.name
                existing.company_id = company.id
            imported += 1
        return imported
