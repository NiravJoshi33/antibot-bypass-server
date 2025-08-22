from abc import ABC, abstractmethod
from typing import Optional

from app.models import ScrapeResponse


class BaseScraper(ABC):
    """Base interface for all scraper services"""

    @abstractmethod
    async def scrape(
        self,
        url: str,
        selector_to_wait_for: Optional[str] = None,
        timeout: int = 30000,
        headless: bool = True,
        **kwargs,
    ) -> ScrapeResponse:
        """Scrape a URL and return structured response"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the scraper"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup the resources"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of scraper service"""
        pass
