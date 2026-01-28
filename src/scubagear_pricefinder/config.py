import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    db_url: str = "sqlite:///./scubagear.db"
    log_level: str = "INFO"
    
    scraper_timeout: int = 10
    scraper_max_retries: int = 3
    scraper_rate_limit_delay: float = 1.0
    
    scheduler_enabled: bool = True
    scheduler_interval_hours: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.info(f"✓ Config loaded: debug={settings.debug}")
