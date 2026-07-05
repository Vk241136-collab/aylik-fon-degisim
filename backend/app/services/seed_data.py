from datetime import date
from decimal import Decimal

from app.domain.models import Fund, FundReport, PortfolioAsset, PortfolioManagementCompany


def asset(report_id, asset_type, name, code, qty, price, mv, weight, sector=None, isin=None, currency="TRY"):
    return PortfolioAsset(
        report_id=report_id,
        asset_type=asset_type,
        asset_name=name,
        asset_code=code,
        ticker=code if asset_type == "Hisse senedi" else None,
        isin=isin,
        currency=currency,
        quantity=Decimal(qty) if qty is not None else None,
        unit_price=Decimal(price) if price is not None else None,
        market_value=Decimal(mv),
        portfolio_weight=Decimal(weight),
        sector=sector,
    )


def scaled_asset(report_id, base, scale):
    asset_type, name, code, qty, price, mv, weight, sector, isin = base
    quantity = str((Decimal(qty) * scale).quantize(Decimal("1"))) if qty is not None else None
    market_value = str((Decimal(mv) * scale).quantize(Decimal("1")))
    return asset(report_id, asset_type, name, code, quantity, price, market_value, weight, sector, isin)


def make_report_pair(fund: Fund, code: str, scale: Decimal):
    may_report = FundReport(
        fund_id=fund.id,
        period="2026-05",
        report_date=date(2026, 5, 31),
        file_name=f"{code.lower()}-mayis.csv",
        file_type="csv",
        file_hash=f"seed-{code.lower()}-may",
        total_value=(Decimal("100000000") * scale).quantize(Decimal("1")),
    )
    june_report = FundReport(
        fund_id=fund.id,
        period="2026-06",
        report_date=date(2026, 6, 30),
        file_name=f"{code.lower()}-haziran.csv",
        file_type="csv",
        file_hash=f"seed-{code.lower()}-june",
        total_value=(Decimal("120000000") * scale).quantize(Decimal("1")),
    )

    may_base = [
        ("Hisse senedi", "Girişim Elektrik Sanayi A.Ş.", "GESAN", "250000", "72", "18000000", "18.00", "Elektrik", None),
        ("Hisse senedi", "Selçuk Ecza Deposu A.Ş.", "SELEC", "400000", "30", "12000000", "12.00", "Sağlık", None),
        ("Hisse senedi", "Aselsan Elektronik Sanayi", "ASELS", "150000", "60", "9000000", "9.00", "Savunma", None),
        ("Hisse senedi", "Tüpraş", "TUPRS", "100000", "160", "16000000", "16.00", "Enerji", None),
        ("Hisse senedi", "BİM Birleşik Mağazalar", "BIMAS", "80000", "250", "20000000", "20.00", "Perakende", None),
        ("Ters repo", "Ters Repo", "TRREP", None, None, "15000000", "15.00", None, None),
        ("Devlet tahvili", "TRT120328T12 Devlet Tahvili", "TRT120328T12", "10000000", "1", "10000000", "10.00", None, "TRT120328T12"),
    ]
    june_base = [
        ("Hisse senedi", "Girişim Elektrik Sanayi A.Ş.", "GESAN", "330000", "78", "25740000", "21.45", "Elektrik", None),
        ("Hisse senedi", "Selçuk Ecza Deposu A.Ş.", "SELEC", "400000", "34", "13600000", "11.33", "Sağlık", None),
        ("Hisse senedi", "Türk Hava Yolları", "THYAO", "60000", "310", "18600000", "15.50", "Ulaştırma", None),
        ("Hisse senedi", "Tüpraş", "TUPRS", "90000", "178", "16020000", "13.35", "Enerji", None),
        ("Hisse senedi", "BİM Birleşik Mağazalar", "BIMAS", "90000", "255", "22950000", "19.13", "Perakende", None),
        ("Nakit", "Nakit", "NAKIT", None, None, "8050000", "6.71", None, None),
        ("Ters repo", "Ters Repo", "TRREP", None, None, "9000000", "7.50", None, None),
        ("Devlet tahvili", "TRT120328T12 Devlet Tahvili", "TRT120328T12", "10000000", "1", "10000000", "8.33", None, "TRT120328T12"),
    ]
    return (
        may_report,
        june_report,
        [scaled_asset(may_report.id, item, scale) for item in may_base],
        [scaled_asset(june_report.id, item, scale) for item in june_base],
    )


company_rows = [
    "Ata Portföy Yönetimi A.Ş.",
    "Ak Portföy Yönetimi A.Ş.",
    "Garanti Portföy Yönetimi A.Ş.",
    "İş Portföy Yönetimi A.Ş.",
    "Yapı Kredi Portföy Yönetimi A.Ş.",
    "QNB Portföy Yönetimi A.Ş.",
]

companies = {company.id: company for company in [PortfolioManagementCompany(name=name) for name in company_rows]}
company_list = list(companies.values())

fund_rows = [
    ("TLY", "TLY Hisse Senedi Yoğun Fon", "Hisse Senedi Fonu", company_list[0].id, "1.00"),
    ("AFT", "Ak Portföy Yeni Teknolojiler Yabancı Hisse Senedi Fonu", "Yabancı Hisse Senedi Fonu", company_list[1].id, "1.45"),
    ("GMR", "Garanti Portföy Birinci Hisse Senedi Fonu", "Hisse Senedi Fonu", company_list[2].id, "0.82"),
    ("TI2", "İş Portföy Hisse Senedi Fonu", "Hisse Senedi Fonu", company_list[3].id, "1.18"),
    ("YAS", "Yapı Kredi Portföy Altın Fonu", "Kıymetli Madenler Fonu", company_list[4].id, "0.74"),
    ("QNB", "QNB Portföy Para Piyasası Fonu", "Para Piyasası Fonu", company_list[5].id, "2.10"),
    ("DBH", "Değişken Borçlanma Araçları Fonu", "Borçlanma Araçları Fonu", company_list[3].id, "0.96"),
    ("KST", "Kısa Vadeli Serbest Fon", "Serbest Fon", company_list[2].id, "1.32"),
    ("NNF", "Hisse Senedi Serbest Fon", "Serbest Fon", company_list[0].id, "0.68"),
    ("MAC", "Marmara Capital Hisse Senedi Fonu", "Hisse Senedi Fonu", company_list[1].id, "1.55"),
]

funds = {}
reports = {}
assets_by_report = {}

for code, name, fund_type, company_id, scale_text in fund_rows:
    fund = Fund(code=code, name=name, fund_type=fund_type, company_id=company_id, source="seed")
    funds[fund.id] = fund
    may_report, june_report, may_assets, june_assets = make_report_pair(fund, code, Decimal(scale_text))
    reports[may_report.id] = may_report
    reports[june_report.id] = june_report
    assets_by_report[may_report.id] = may_assets
    assets_by_report[june_report.id] = june_assets

comparisons = {}
comparison_results = {}
