from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.enums import ChangeStatus


@dataclass(slots=True)
class PortfolioManagementCompany:
    name: str
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class Fund:
    code: str
    name: str
    company_id: UUID
    fund_type: str | None = None
    source: str | None = None
    kap_url: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass(slots=True)
class FundReport:
    fund_id: UUID
    period: str
    report_date: date
    file_name: str
    file_type: str
    file_hash: str
    total_value: Decimal | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class PortfolioAsset:
    report_id: UUID
    asset_type: str
    asset_name: str
    id: UUID = field(default_factory=uuid4)
    asset_subtype: str | None = None
    asset_code: str | None = None
    ticker: str | None = None
    isin: str | None = None
    issuer_name: str | None = None
    currency: str | None = None
    quantity: Decimal | None = None
    nominal_value: Decimal | None = None
    unit_price: Decimal | None = None
    market_value: Decimal | None = None
    portfolio_weight: Decimal | None = None
    fund_total_weight: Decimal | None = None
    maturity_date: date | None = None
    interest_rate: Decimal | None = None
    contract_code: str | None = None
    sector: str | None = None
    raw_row_data: dict = field(default_factory=dict)


@dataclass(slots=True)
class ComparisonAssetResult:
    asset_key: str
    asset_name: str
    asset_type: str
    previous_asset: PortfolioAsset | None
    current_asset: PortfolioAsset | None
    match_confidence: int
    match_method: str
    statuses: list[ChangeStatus]
    quantity_delta: Decimal | None = None
    quantity_change_pct: Decimal | None = None
    market_value_delta: Decimal | None = None
    market_value_change_pct: Decimal | None = None
    weight_delta_pp: Decimal | None = None
    weight_change_pct: Decimal | None = None
    transaction_effect: Decimal | None = None
    price_effect: Decimal | None = None
    unit_price_is_estimated: bool = False


@dataclass(slots=True)
class Comparison:
    fund_id: UUID
    previous_report_id: UUID
    current_report_id: UUID
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
