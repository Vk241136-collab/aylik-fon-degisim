from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pandas as pd

from app.core.decimal_utils import parse_decimal
from app.core.normalization import looks_like_total_row
from app.domain.models import PortfolioAsset
from app.services.column_mapper import suggest_mapping


class OCRService:
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError("OCR desteği ayrı servis olarak eklenecek.")


class PortfolioParser:
    supported_extensions = {".csv", ".xlsx", ".xls", ".pdf"}

    def parse(self, file_path: str, report_id: UUID, mapping: dict[str, str] | None = None) -> tuple[list[PortfolioAsset], dict[str, str]]:
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError("Desteklenmeyen dosya türü.")

        frame = self._read_frame(path)
        frame = frame.dropna(how="all")
        headers = [str(column) for column in frame.columns]
        resolved_mapping = mapping or suggest_mapping(headers)
        assets = [asset for _, row in frame.iterrows() if (asset := self._row_to_asset(row, report_id, resolved_mapping))]
        return assets, resolved_mapping

    def _read_frame(self, path: Path) -> pd.DataFrame:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(path)
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path)
        if suffix == ".pdf":
            return self._read_pdf(path)
        raise ValueError("Desteklenmeyen dosya türü.")

    def _read_pdf(self, path: Path) -> pd.DataFrame:
        import pdfplumber

        rows: list[list[str]] = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    rows.extend(table)
        if not rows:
            raise ValueError("PDF içinde tablo bulunamadı. Manuel kolon eşleme gerekli.")
        header, *data = rows
        return pd.DataFrame(data, columns=header)

    def _row_to_asset(self, row: pd.Series, report_id: UUID, mapping: dict[str, str]) -> PortfolioAsset | None:
        def get(field: str) -> object | None:
            source = mapping.get(field)
            return row.get(source) if source else None

        asset_name = str(get("asset_name") or "").strip()
        if not asset_name or looks_like_total_row(asset_name):
            return None

        return PortfolioAsset(
            report_id=report_id,
            asset_type=str(get("asset_type") or "Diğer yatırım araçları").strip(),
            asset_name=asset_name,
            asset_code=str(get("asset_code") or "").strip() or None,
            ticker=str(get("ticker") or get("asset_code") or "").strip() or None,
            isin=str(get("isin") or "").strip() or None,
            issuer_name=str(get("issuer_name") or "").strip() or None,
            currency=str(get("currency") or "TRY").strip() or None,
            quantity=parse_decimal(get("quantity")),
            nominal_value=parse_decimal(get("nominal_value")),
            unit_price=parse_decimal(get("unit_price")),
            market_value=parse_decimal(get("market_value")),
            portfolio_weight=parse_decimal(get("portfolio_weight") or get("fund_total_weight")),
            fund_total_weight=parse_decimal(get("fund_total_weight")),
            interest_rate=parse_decimal(get("interest_rate")),
            contract_code=str(get("contract_code") or "").strip() or None,
            sector=str(get("sector") or "").strip() or None,
            raw_row_data={str(key): (None if pd.isna(value) else value) for key, value in row.to_dict().items()},
        )
