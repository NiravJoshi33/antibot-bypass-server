from typing import Dict
from app.services.base import BaseScraper
from app.services.brightdata import BrightDataCDPScraper
from app.models import ScraperType
from app.services.camoufox_scraper import CamoufoxScraper


class ScraperFactory:
    """Factory for creating scraper instances"""

    _scrapers: Dict[ScraperType, BaseScraper] = {}
    _initialized = False

    @classmethod
    async def initialize(cls):
        """Initialize all scraper services"""
        if cls._initialized:
            return

        # Initialize BrightData scraper
        brightdata_scraper = BrightDataCDPScraper()
        camoufox_scraper = CamoufoxScraper()
        await brightdata_scraper.initialize()
        await camoufox_scraper.initialize()
        cls._scrapers[ScraperType.BRIGHTDATA_CDP] = brightdata_scraper
        cls._scrapers[ScraperType.CAMOUFOX] = camoufox_scraper

        # Add future scrapers here
        # selenium_scraper = SeleniumScraper()
        # await selenium_scraper.initialize()
        # cls._scrapers[ScraperType.SELENIUM_GRID] = selenium_scraper

        cls._initialized = True

    @classmethod
    async def cleanup(cls):
        """Clean up all scraper services"""
        for scraper in cls._scrapers.values():
            await scraper.cleanup()
        cls._scrapers.clear()
        cls._initialized = False

    @classmethod
    def get_scraper(cls, scraper_type: ScraperType) -> BaseScraper:
        """Get a scraper instance by type"""
        if not cls._initialized:
            raise RuntimeError("ScraperFactory not initialized")

        scraper = cls._scrapers.get(scraper_type)
        if not scraper:
            raise ValueError(f"Scraper type {scraper_type} not available")

        return scraper

    @classmethod
    def get_available_scrapers(cls) -> list[str]:
        """Get list of available scraper types"""
        return [scraper_type.value for scraper_type in cls._scrapers.keys()]
