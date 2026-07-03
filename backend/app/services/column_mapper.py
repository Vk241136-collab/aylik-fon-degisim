from rapidfuzz import fuzz, process

from app.core.normalization import normalize_text


CANONICAL_COLUMNS = {
    "asset_name": ["MENKUL KIYMET", "VARLIK ADI", "KIYMET", "UNVAN", "ACIKLAMA"],
    "asset_code": ["MENKUL KIYMET KODU", "VARLIK KODU", "KIYMET KODU", "KOD"],
    "ticker": ["HISSE KODU", "BIST KODU", "TICKER", "PAY KODU"],
    "isin": ["ISIN", "ISIN KODU"],
    "issuer_name": ["IHRACCI", "IHRACCI UNVANI", "KURUM"],
    "asset_type": ["VARLIK TURU", "MENKUL TURU", "GRUP", "TUR"],
    "quantity": ["ADET", "MIKTAR", "PAY ADEDI"],
    "nominal_value": ["NOMINAL DEGER", "NOMINAL"],
    "unit_price": ["BIRIM FIYAT", "FIYAT"],
    "market_value": ["PIYASA DEGERI", "RAYIC DEGER", "DEGER"],
    "currency": ["DOVIZ CINSI", "PARA BIRIMI", "DOVIZ"],
    "portfolio_weight": ["PORTFOY ORANI", "PORTFOY DEGERI ORANI", "ORAN"],
    "fund_total_weight": ["FON TOPLAM DEGERINE ORANI", "NET AKTIF DEGERE ORANI"],
    "maturity_date": ["VADE", "VADE TARIHI"],
    "interest_rate": ["FAIZ ORANI", "KUPON ORANI"],
    "contract_code": ["SOZLESME KODU", "KONTRAT KODU"],
    "sector": ["SEKTOR"],
}


def suggest_mapping(headers: list[str]) -> dict[str, str]:
    normalized_to_original = {normalize_text(header): header for header in headers}
    choices = list(normalized_to_original.keys())
    mapping: dict[str, str] = {}
    for canonical, aliases in CANONICAL_COLUMNS.items():
        candidates = [normalize_text(alias) for alias in aliases]
        best = None
        best_score = 0
        for alias in candidates:
            match = process.extractOne(alias, choices, scorer=fuzz.token_sort_ratio)
            if match and match[1] > best_score:
                best = match[0]
                best_score = match[1]
        if best and best_score >= 72:
            mapping[canonical] = normalized_to_original[best]
    return mapping
