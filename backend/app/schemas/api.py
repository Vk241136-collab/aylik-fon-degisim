from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str


class CompanyRead(CompanyCreate):
    id: UUID


class FundCreate(BaseModel):
    code: str
    name: str
    company_id: UUID
    fund_type: str | None = None
    source: str | None = None
    kap_url: str | None = None


class FundRead(FundCreate):
    id: UUID


class ReportRead(BaseModel):
    id: UUID
    fund_id: UUID
    period: str
    report_date: date
    file_name: str
    file_type: str
    total_value: Decimal | None
    created_at: datetime
    parsed_row_count: int = 0
    error_count: int = 0
    parse_status: str = "PARSED"


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    asset_type: str
    asset_name: str
    asset_code: str | None = None
    ticker: str | None = None
    isin: str | None = None
    issuer_name: str | None = None
    currency: str | None = None
    quantity: Decimal | None = None
    unit_price: Decimal | None = None
    market_value: Decimal | None = None
    portfolio_weight: Decimal | None = None
    sector: str | None = None


class ComparisonCreate(BaseModel):
    fund_id: UUID
    previous_report_id: UUID
    current_report_id: UUID


class ComparisonRead(ComparisonCreate):
    id: UUID
    created_at: datetime


class ComparisonAssetRead(BaseModel):
    asset_key: str
    asset_name: str
    asset_type: str
    match_confidence: int
    match_method: str
    statuses: list[str]
    status_labels: list[str]
    previous_quantity: Decimal | None
    current_quantity: Decimal | None
    quantity_delta: Decimal | None
    quantity_change_pct: Decimal | None
    previous_market_value: Decimal | None
    current_market_value: Decimal | None
    market_value_delta: Decimal | None
    market_value_change_pct: Decimal | None
    previous_weight: Decimal | None
    current_weight: Decimal | None
    weight_delta_pp: Decimal | None
    weight_change_pct: Decimal | None
    transaction_effect: Decimal | None
    price_effect: Decimal | None
    unit_price_is_estimated: bool


class ComparisonSummary(BaseModel):
    fund_code: str
    fund_name: str
    company_name: str
    previous_period: str
    current_period: str
    previous_total_value: Decimal | None
    current_total_value: Decimal | None
    total_value_delta: Decimal | None
    equity_weight_previous: Decimal
    equity_weight_current: Decimal
    equity_weight_delta_pp: Decimal
    new_count: int
    exited_count: int
    increased_count: int
    decreased_count: int
    largest_position: str | None
    largest_new_position: str | None
    top_increased_position: str | None
    top_decreased_position: str | None
    concentration_hhi_previous: Decimal
    concentration_hhi_current: Decimal
    analysis_text: str


class ChartsPayload(BaseModel):
    asset_class_distribution: list[dict]
    top_assets: list[dict]
    weight_increases: list[dict]
    weight_decreases: list[dict]
    currency_distribution: list[dict]


class KapSyncStatusRead(BaseModel):
    enabled: bool
    last_started_at: datetime | None
    last_finished_at: datetime | None
    last_status: str
    last_message: str | None
    discovered_funds: int
    discovered_disclosures: int
    downloaded_reports: int
    parse_jobs_created: int
    errors: list[str]
