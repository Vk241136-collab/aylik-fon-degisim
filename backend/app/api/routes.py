from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import csv
from io import StringIO

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import get_settings
from app.core.decimal_utils import delta
from app.domain.enums import STATUS_LABELS_TR, ChangeStatus
from app.domain.models import Comparison, Fund, FundReport
from app.schemas.api import (
    AssetRead,
    ChartsPayload,
    CompanyCreate,
    CompanyRead,
    ComparisonAssetRead,
    ComparisonCreate,
    ComparisonRead,
    ComparisonSummary,
    FundCreate,
    FundRead,
    KapSyncStatusRead,
    ReportRead,
)
from app.services.comparison_engine import ComparisonEngine, hhi
from app.services.file_security import validate_upload
from app.services.kap_sync import KapSyncService, kap_sync_state
from app.services.parser import PortfolioParser
from app.services.seed_data import assets_by_report, companies, comparison_results, comparisons, funds, reports

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/kap/status", response_model=KapSyncStatusRead)
def kap_status():
    return kap_sync_state


@router.post("/kap/sync", response_model=KapSyncStatusRead)
async def kap_sync_once():
    return await KapSyncService().run_once()


@router.post("/companies", response_model=CompanyRead)
def create_company(payload: CompanyCreate):
    company = CompanyRead(id=uuid4(), name=payload.name)
    companies[company.id] = company
    return company


@router.get("/companies", response_model=list[CompanyRead])
def list_companies():
    return list(companies.values())


@router.post("/funds", response_model=FundRead)
def create_fund(payload: FundCreate):
    fund = Fund(code=payload.code.upper(), name=payload.name, company_id=payload.company_id)
    funds[fund.id] = fund
    return fund


@router.get("/funds", response_model=list[FundRead])
def list_funds(search: str | None = None, limit: int = Query(250, ge=1, le=2000), offset: int = Query(0, ge=0)):
    rows = sorted(funds.values(), key=lambda item: item.code)
    if search:
        needle = search.upper()
        rows = [fund for fund in rows if needle in fund.code.upper() or needle in fund.name.upper()]
    return rows[offset : offset + limit]


@router.post("/funds/import-catalog")
async def import_fund_catalog(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Fon kataloğu dosyası çok büyük.")
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Fon kataloğu CSV formatında olmalı.")

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    imported = 0
    for row in reader:
        code = (row.get("code") or row.get("Fon Kodu") or row.get("fon_kodu") or "").strip().upper()
        name = (row.get("name") or row.get("Fon Adı") or row.get("fon_adi") or "").strip()
        company_name = (row.get("company") or row.get("Kurucu") or row.get("portfoy_yonetim_sirketi") or "Bilinmeyen Portföy").strip()
        if not code or not name:
            continue
        company = next((item for item in companies.values() if item.name == company_name), None)
        if company is None:
            company = CompanyRead(id=uuid4(), name=company_name)
            companies[company.id] = company
        existing = next((item for item in funds.values() if item.code == code), None)
        if existing:
            existing.name = name
            existing.company_id = company.id
        else:
            fund = Fund(code=code, name=name, company_id=company.id)
            funds[fund.id] = fund
        imported += 1
    return {"imported": imported, "total_funds": len(funds)}


@router.get("/funds/{fund_id}", response_model=FundRead)
def get_fund(fund_id: UUID):
    return _get(funds, fund_id, "Fon bulunamadı.")


@router.post("/funds/{fund_id}/reports", response_model=ReportRead)
async def upload_report(fund_id: UUID, period: str, report_date: date, file: UploadFile = File(...)):
    if fund_id not in funds:
        raise HTTPException(404, "Fon bulunamadı.")
    content = await file.read()
    try:
        file_hash = validate_upload(file, content, get_settings().max_upload_size_mb)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if any(report.file_hash == file_hash for report in reports.values()):
        raise HTTPException(409, "Bu dosya daha önce yüklenmiş.")

    upload_dir = get_settings().upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4()}{Path(file.filename or '').suffix.lower()}"
    file_path = upload_dir / safe_name
    file_path.write_bytes(content)
    report = FundReport(
        fund_id=fund_id,
        period=period,
        report_date=report_date,
        file_name=file.filename or safe_name,
        file_type=Path(file.filename or "").suffix.lower().removeprefix("."),
        file_hash=file_hash,
    )
    reports[report.id] = report
    assets_by_report[report.id] = []
    return _report_read(report)


@router.get("/funds/{fund_id}/reports", response_model=list[ReportRead])
def list_reports(fund_id: UUID):
    return [_report_read(report) for report in reports.values() if report.fund_id == fund_id]


@router.get("/reports/{report_id}", response_model=ReportRead)
def get_report(report_id: UUID):
    return _report_read(_get(reports, report_id, "Rapor bulunamadı."))


@router.delete("/reports/{report_id}")
def delete_report(report_id: UUID):
    reports.pop(report_id, None)
    assets_by_report.pop(report_id, None)
    return {"deleted": True}


@router.post("/reports/{report_id}/parse")
def parse_report(report_id: UUID, file_path: str, mapping: dict[str, str] | None = None):
    if report_id not in reports:
        raise HTTPException(404, "Rapor bulunamadı.")
    try:
        assets, resolved_mapping = PortfolioParser().parse(file_path, report_id, mapping)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    assets_by_report[report_id] = assets
    return {"status": "PARSED", "row_count": len(assets), "mapping": resolved_mapping}


@router.get("/reports/{report_id}/assets", response_model=list[AssetRead])
def list_assets(report_id: UUID):
    return assets_by_report.get(report_id, [])


@router.put("/reports/{report_id}/assets/{asset_id}", response_model=AssetRead)
def update_asset(report_id: UUID, asset_id: UUID, payload: AssetRead):
    assets = assets_by_report.get(report_id, [])
    for index, asset in enumerate(assets):
        if asset.id == asset_id:
            assets[index] = payload
            return payload
    raise HTTPException(404, "Varlık bulunamadı.")


@router.post("/comparisons", response_model=ComparisonRead)
def create_comparison(payload: ComparisonCreate):
    if payload.previous_report_id not in assets_by_report or payload.current_report_id not in assets_by_report:
        raise HTTPException(404, "Karşılaştırılacak rapor bulunamadı.")
    comparison = Comparison(
        fund_id=payload.fund_id,
        previous_report_id=payload.previous_report_id,
        current_report_id=payload.current_report_id,
    )
    comparisons[comparison.id] = comparison
    comparison_results[comparison.id] = ComparisonEngine().compare(
        assets_by_report[payload.previous_report_id],
        assets_by_report[payload.current_report_id],
    )
    return comparison


@router.get("/comparisons/{comparison_id}", response_model=ComparisonRead)
def get_comparison(comparison_id: UUID):
    return _get(comparisons, comparison_id, "Karşılaştırma bulunamadı.")


@router.get("/comparisons/{comparison_id}/assets", response_model=list[ComparisonAssetRead])
def get_comparison_assets(comparison_id: UUID):
    _ensure_comparison(comparison_id)
    return [_comparison_asset_read(result) for result in comparison_results[comparison_id]]


@router.get("/comparisons/{comparison_id}/summary", response_model=ComparisonSummary)
def get_summary(comparison_id: UUID):
    comparison = _ensure_comparison(comparison_id)
    fund = funds[comparison.fund_id]
    company = companies[fund.company_id]
    previous_report = reports[comparison.previous_report_id]
    current_report = reports[comparison.current_report_id]
    previous_assets = assets_by_report[comparison.previous_report_id]
    current_assets = assets_by_report[comparison.current_report_id]
    results = comparison_results[comparison_id]
    equity_prev = _sum_weight(previous_assets, "Hisse senedi")
    equity_cur = _sum_weight(current_assets, "Hisse senedi")
    largest = max(current_assets, key=lambda asset: asset.portfolio_weight or Decimal("0"), default=None)
    new_positions = [r for r in results if ChangeStatus.NEW_POSITION in r.statuses]
    increased = [r for r in results if ChangeStatus.WEIGHT_INCREASED in r.statuses]
    decreased = [r for r in results if ChangeStatus.WEIGHT_DECREASED in r.statuses]
    summary = ComparisonSummary(
        fund_code=fund.code,
        fund_name=fund.name,
        company_name=company.name,
        previous_period=previous_report.period,
        current_period=current_report.period,
        previous_total_value=previous_report.total_value,
        current_total_value=current_report.total_value,
        total_value_delta=delta(previous_report.total_value, current_report.total_value),
        equity_weight_previous=equity_prev,
        equity_weight_current=equity_cur,
        equity_weight_delta_pp=equity_cur - equity_prev,
        new_count=len(new_positions),
        exited_count=sum(ChangeStatus.EXITED_POSITION in r.statuses for r in results),
        increased_count=len(increased),
        decreased_count=len(decreased),
        largest_position=largest.asset_name if largest else None,
        largest_new_position=max(new_positions, key=lambda r: r.current_asset.portfolio_weight if r.current_asset else Decimal("0"), default=None).asset_name if new_positions else None,
        top_increased_position=max(increased, key=lambda r: r.weight_delta_pp or Decimal("0"), default=None).asset_name if increased else None,
        top_decreased_position=min(decreased, key=lambda r: r.weight_delta_pp or Decimal("0"), default=None).asset_name if decreased else None,
        concentration_hhi_previous=hhi(previous_assets),
        concentration_hhi_current=hhi(current_assets),
        analysis_text="",
    )
    summary.analysis_text = _analysis_text(summary)
    return summary


@router.get("/comparisons/{comparison_id}/charts", response_model=ChartsPayload)
def get_charts(comparison_id: UUID):
    comparison = _ensure_comparison(comparison_id)
    previous_assets = assets_by_report[comparison.previous_report_id]
    current_assets = assets_by_report[comparison.current_report_id]
    results = comparison_results[comparison_id]
    return ChartsPayload(
        asset_class_distribution=_asset_class_distribution(previous_assets, current_assets),
        top_assets=sorted(
            [{"name": a.asset_name, "weight": a.portfolio_weight or Decimal("0"), "type": a.asset_type} for a in current_assets],
            key=lambda item: item["weight"],
            reverse=True,
        )[:10],
        weight_increases=_result_weight_changes(results, reverse=True)[:10],
        weight_decreases=_result_weight_changes(results, reverse=False)[:10],
        currency_distribution=_currency_distribution(current_assets),
    )


@router.get("/comparisons/{comparison_id}/export")
def export_comparison(comparison_id: UUID, format: str = "csv"):
    rows = get_comparison_assets(comparison_id)
    if format != "csv":
        raise HTTPException(501, "Bu MVP'de CSV dışa aktarma hazır; Excel ve PDF için servis sınırları oluşturuldu.")
    lines = ["asset_name,asset_type,statuses,previous_weight,current_weight,weight_delta_pp"]
    for row in rows:
        lines.append(f"{row.asset_name},{row.asset_type},{'|'.join(row.status_labels)},{row.previous_weight},{row.current_weight},{row.weight_delta_pp}")
    return StreamingResponse(iter(["\n".join(lines)]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=comparison.csv"})


@router.post("/comparisons/{comparison_id}/resolve-match")
def resolve_match(comparison_id: UUID):
    _ensure_comparison(comparison_id)
    return {"status": "saved"}


@router.get("/funds/{fund_id}/timeline")
def fund_timeline(fund_id: UUID):
    fund_reports = sorted([report for report in reports.values() if report.fund_id == fund_id], key=lambda item: item.report_date)
    return [{"period": report.period, "total_value": report.total_value, "asset_count": len(assets_by_report.get(report.id, []))} for report in fund_reports]


@router.get("/funds/{fund_id}/assets/{asset_code}/timeline")
def asset_timeline(fund_id: UUID, asset_code: str):
    items = []
    for report in sorted([r for r in reports.values() if r.fund_id == fund_id], key=lambda item: item.report_date):
        for asset in assets_by_report.get(report.id, []):
            if (asset.asset_code or "").upper() == asset_code.upper() or (asset.ticker or "").upper() == asset_code.upper():
                items.append({"period": report.period, "weight": asset.portfolio_weight, "quantity": asset.quantity, "market_value": asset.market_value})
    return items


def _get(store, key, message):
    try:
        return store[key]
    except KeyError as exc:
        raise HTTPException(404, message) from exc


def _ensure_comparison(comparison_id: UUID):
    comparison = _get(comparisons, comparison_id, "Karşılaştırma bulunamadı.")
    if comparison_id not in comparison_results:
        comparison_results[comparison_id] = ComparisonEngine().compare(
            assets_by_report[comparison.previous_report_id], assets_by_report[comparison.current_report_id]
        )
    return comparison


def _report_read(report: FundReport) -> ReportRead:
    return ReportRead(
        id=report.id,
        fund_id=report.fund_id,
        period=report.period,
        report_date=report.report_date,
        file_name=report.file_name,
        file_type=report.file_type,
        total_value=report.total_value,
        created_at=report.created_at,
        parsed_row_count=len(assets_by_report.get(report.id, [])),
    )


def _comparison_asset_read(result) -> ComparisonAssetRead:
    return ComparisonAssetRead(
        asset_key=result.asset_key,
        asset_name=result.asset_name,
        asset_type=result.asset_type,
        match_confidence=result.match_confidence,
        match_method=result.match_method,
        statuses=[status.value for status in result.statuses],
        status_labels=[STATUS_LABELS_TR[status] for status in result.statuses],
        previous_quantity=result.previous_asset.quantity if result.previous_asset else None,
        current_quantity=result.current_asset.quantity if result.current_asset else None,
        quantity_delta=result.quantity_delta,
        quantity_change_pct=result.quantity_change_pct,
        previous_market_value=result.previous_asset.market_value if result.previous_asset else None,
        current_market_value=result.current_asset.market_value if result.current_asset else None,
        market_value_delta=result.market_value_delta,
        market_value_change_pct=result.market_value_change_pct,
        previous_weight=result.previous_asset.portfolio_weight if result.previous_asset else None,
        current_weight=result.current_asset.portfolio_weight if result.current_asset else None,
        weight_delta_pp=result.weight_delta_pp,
        weight_change_pct=result.weight_change_pct,
        transaction_effect=result.transaction_effect,
        price_effect=result.price_effect,
        unit_price_is_estimated=result.unit_price_is_estimated,
    )


def _sum_weight(assets, asset_type):
    return sum((asset.portfolio_weight or Decimal("0") for asset in assets if asset.asset_type == asset_type), Decimal("0"))


def _analysis_text(summary: ComparisonSummary) -> str:
    return (
        f"{summary.fund_code} fonunun {summary.current_period} portföy dağılımı {summary.previous_period} dönemiyle karşılaştırıldığında, "
        f"hisse senedi ağırlığının %{summary.equity_weight_previous:.2f} seviyesinden %{summary.equity_weight_current:.2f} seviyesine geldiği görülmektedir. "
        f"Portföye {summary.new_count} yeni varlık girerken {summary.exited_count} varlık portföyden çıkmıştır. "
        "Adet ve fiyat etkileri ayrı hesaplandığından, ağırlık değişimleri tek başına alım-satım yorumu olarak değerlendirilmemelidir."
    )


def _asset_class_distribution(previous, current):
    labels = sorted({asset.asset_type for asset in previous + current})
    return [{"asset_type": label, "previous": _sum_weight(previous, label), "current": _sum_weight(current, label)} for label in labels]


def _result_weight_changes(results, reverse):
    filtered = [r for r in results if r.weight_delta_pp is not None]
    return [
        {"name": r.asset_name, "delta": r.weight_delta_pp, "current": r.current_asset.portfolio_weight if r.current_asset else None}
        for r in sorted(filtered, key=lambda item: item.weight_delta_pp, reverse=reverse)
    ]


def _currency_distribution(assets):
    totals: dict[str, Decimal] = {}
    for asset in assets:
        totals[asset.currency or "Bilinmiyor"] = totals.get(asset.currency or "Bilinmiyor", Decimal("0")) + (asset.portfolio_weight or Decimal("0"))
    return [{"currency": key, "weight": value} for key, value in totals.items()]
