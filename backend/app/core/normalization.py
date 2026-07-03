import re
import unicodedata


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.upper()
    text = text.translate(str.maketrans({"İ": "I", "I": "I", "Ş": "S", "Ğ": "G", "Ü": "U", "Ö": "O", "Ç": "C"}))
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_code(value: str | None) -> str:
    return normalize_text(value).replace(" ", "")


def looks_like_total_row(name: str | None) -> bool:
    normalized = normalize_text(name)
    return any(token in normalized for token in ("TOPLAM", "GENEL TOPLAM", "PORTFOY TOPLAMI"))
