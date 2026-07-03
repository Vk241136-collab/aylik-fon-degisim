from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class KapSyncState:
    enabled: bool
    last_started_at: datetime | None = None
    last_finished_at: datetime | None = None
    last_status: str = "NOT_RUN"
    last_message: str | None = None
    discovered_funds: int = 0
    discovered_disclosures: int = 0
    downloaded_reports: int = 0
    parse_jobs_created: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class KapFundRecord:
    code: str
    name: str
    fund_type: str | None = None
    company_name: str | None = None
    kap_url: str | None = None


@dataclass(slots=True)
class KapDisclosureRecord:
    fund_code: str
    title: str
    published_at: datetime | None = None
    disclosure_type: str | None = None
    attachment_url: str | None = None
    source_url: str | None = None
