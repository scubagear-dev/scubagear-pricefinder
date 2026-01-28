import httpx
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.scubagear_pricefinder.config import settings

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    
    def __init__(self, retailer_id: str, base_url: str):
        self.retailer_id = retailer_id
        self.base_url = base_url
        self.client = httpx.Client(
            timeout=settings.scraper_timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/120.0.0.0 Safari/537.36"
            },
            follow_redirects=True,
        )
        self.last_request_time = 0.0
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        delay = max(0, settings.scraper_rate_limit_delay - elapsed)
        if delay > 0:
            time.sleep(delay)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(settings.scraper_max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    def _fetch(self, url: str) -> str:
        self._rate_limit()
        logger.debug(f"Fetching: {url}")
        response = self.client.get(url)
        response.raise_for_status()
        return response.text
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        pass
    
    def __del__(self):
        try:
            self.client.close()
        except:
            pass
