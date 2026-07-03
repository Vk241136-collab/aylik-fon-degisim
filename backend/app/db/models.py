from decimal import Decimal
from uuid import UUID as PyUUID

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class PortfolioManagementCompanyORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "portfolio_management_companies"
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class FundORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "funds"
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolio_management_companies.id"), index=True)
    company = relationship("PortfolioManagementCompanyORM")


class FundReportORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "fund_reports"
    fund_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("funds.id"), index=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)
    report_date: Mapped[object] = mapped_column(Date, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    parse_status: Mapped[str] = mapped_column(String(30), default="UPLOADED")
    parsed_row_count: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    total_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6), nullable=True)

    __table_args__ = (UniqueConstraint("fund_id", "period", "deleted_at", name="uq_fund_period_active_report"),)


class PortfolioAssetORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "portfolio_assets"
    report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)
    asset_type: Mapped[str] = mapped_column(String(120), index=True)
    asset_subtype: Mapped[str | None] = mapped_column(String(120))
    asset_name: Mapped[str] = mapped_column(String(500), nullable=False)
    asset_code: Mapped[str | None] = mapped_column(String(80), index=True)
    ticker: Mapped[str | None] = mapped_column(String(40), index=True)
    isin: Mapped[str | None] = mapped_column(String(40), index=True)
    issuer_name: Mapped[str | None] = mapped_column(String(255))
    currency: Mapped[str | None] = mapped_column(String(12))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(24, 6))
    nominal_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    market_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 6))
    portfolio_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    fund_total_weight: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    raw_row_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    __table_args__ = (Index("ix_assets_report_type_code", "report_id", "asset_type", "asset_code"),)


class ComparisonORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "comparisons"
    fund_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("funds.id"), index=True)
    previous_report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)
    current_report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)


class ComparisonAssetResultORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "comparison_asset_results"
    comparison_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comparisons.id"), index=True)
    asset_type: Mapped[str] = mapped_column(String(120), index=True)
    asset_name: Mapped[str] = mapped_column(String(500))
    statuses: Mapped[list[str]] = mapped_column(JSONB)
    result_payload: Mapped[dict] = mapped_column(JSONB)


class ImportJobORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "import_jobs"
    report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)


class ParsingErrorORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "parsing_errors"
    report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)
    row_number: Mapped[int | None] = mapped_column()
    message: Mapped[str] = mapped_column(Text)


class UserColumnMappingORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "user_column_mappings"
    report_id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fund_reports.id"), index=True)
    mapping: Mapped[dict] = mapped_column(JSONB, default=dict)
