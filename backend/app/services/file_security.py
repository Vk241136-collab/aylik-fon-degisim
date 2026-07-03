from pathlib import Path
import hashlib

from fastapi import UploadFile

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".csv"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def validate_upload(file: UploadFile, content: bytes, max_size_mb: int) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Bu dosya türü desteklenmiyor.")
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValueError("Dosya MIME türü geçerli değil.")
    if len(content) > max_size_mb * 1024 * 1024:
        raise ValueError("Dosya boyutu sınırı aşıldı.")
    if "/" in (file.filename or "") or "\\" in (file.filename or ""):
        raise ValueError("Dosya adı güvenli değil.")
    return hashlib.sha256(content).hexdigest()
