from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Aylık Fon Değişim"
    public_site_url: str = "https://aylıkfondeğişim.com"
    public_site_idn: str = "xn--aylkfondeiim-lyb9vxz.com"
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/fund_analyzer"
    upload_dir: Path = Path("storage/uploads")
    max_upload_size_mb: int = 25
    cors_origins: list[str] = ["http://localhost:3000"]
    kap_base_url: str = "https://www.kap.org.tr"
    kap_sync_enabled: bool = False
    kap_poll_interval_minutes: int = 30
    kap_request_timeout_seconds: int = 20
    kap_user_agent: str = "AylikFonDegisimBot/0.1 contact:info@aylikfondegisim.com"
    weight_total_tolerance_pp: float = 0.5
    market_value_tolerance_pct: float = 0.5

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
