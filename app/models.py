from typing import Dict, List
from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl  # type: ignore[import-not-found]

from app.constants.app_data import AppData


class ScraperType(str, Enum):
    BRIGHTDATA_CDP = "brightdata_cdp"
    CAMOUFOX = "camoufox"


class ScrapeRequest(BaseModel):
    url: HttpUrl
    scraper_type: ScraperType = ScraperType.BRIGHTDATA_CDP
    selector_to_wait_for: Optional[str] = None
    timeout: Optional[int] = None
    headless: bool = True
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy_url: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    proxy_server: Optional[str] = None


class ScrapeResponse(BaseModel):
    success: bool
    html: Optional[str] = None
    error: Optional[str] = None
    content_length: Optional[int] = None
    execution_time: float
    scraper_used: ScraperType
    retries_attempted: int
    cookies: Optional[Dict[str, str]] = None  


class HealthResponse(BaseModel):
    status: str
    version: str = AppData.app_version
    available_scrapers: List[str] = [ScraperType.BRIGHTDATA_CDP, ScraperType.CAMOUFOX]
