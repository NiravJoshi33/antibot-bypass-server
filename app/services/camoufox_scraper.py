import asyncio
import logging
import random
import time
from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Browser, Page, ViewportSize
from typing import Optional, Tuple, Dict
from app.models import ScraperType, ScrapeResponse
from app.services.base import BaseScraper

logger = logging.getLogger(__name__)

BROWSER_SEMAPHORE = asyncio.Semaphore(5)

class CamoufoxScraper(BaseScraper):
    def __init__(self) -> None:
        # Don't store instances as class attributes - use them per request
        pass

    @property
    def name(self) -> ScraperType:
        return ScraperType.CAMOUFOX

    async def initialize(self) -> None:
        """Initialize Camoufox scraper (no persistent state needed)"""
        logger.info("Camoufox Scraper initialized")

    async def cleanup(self) -> None:
        """Cleanup (no persistent state to clean)"""
        logger.info("Camoufox Scraper cleaned up")

    async def scrape(
        self,
        url: str,
        selector_to_wait_for: Optional[str] = None,
        timeout: int = 30000,
        headless: bool = True,
        proxy_url: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        proxy_server: Optional[str] = None,
        **kwargs,
    ) -> ScrapeResponse:
        start_time = time.time()
        retries = 0

        max_retries = 3

        for attempt in range(max_retries + 1):
            try:
                async with BROWSER_SEMAPHORE:
                    content, cookies = await self._scrape_with_camoufox(
                        url,
                        selector_to_wait_for,
                        timeout,
                        headless,
                        proxy_url,
                        proxy_username,
                        proxy_password,
                        proxy_server,
                    )

                execution_time = time.time() - start_time
                content_length = len(content) if content else 0

                # Validate content quality
                if content_length < 10000:
                    logger.warning(
                        f"Content too short ({content_length} chars) for {url}"
                    )
                    if attempt < max_retries:
                        retries += 1
                        await asyncio.sleep(2**attempt)
                        continue

                return ScrapeResponse(
                    success=True,
                    html=content,
                    cookies=cookies,
                    content_length=content_length,
                    execution_time=execution_time,
                    scraper_used=self.name,
                    retries_attempted=retries,
                )

            except Exception as e:
                logger.error(f"Camoufox attempt {attempt + 1} failed for {url}: {e}")
                retries += 1

                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

        execution_time = time.time() - start_time
        return ScrapeResponse(
            success=False,
            error="Max retries exceeded",
            execution_time=execution_time,
            scraper_used=self.name,
            retries_attempted=retries,
        )

    async def _scrape_with_camoufox(
        self,
        url: str,
        selector_to_wait_for: Optional[str] = None,
        timeout: int = 30000,
        headless: bool = True,
        proxy_url: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        proxy_server: Optional[str] = None,
    ) -> Tuple[str, Dict[str, str]]:
        """Scrape with proper Camoufox usage and typing"""

        if proxy_server and proxy_username and proxy_password:
            logger.info(f"Using proxy: {proxy_server}")
            proxy = {
                "server": proxy_server,
                "username": proxy_username,
                "password": proxy_password,
            }
            geoip = True
        else:
            proxy = None
            geoip = False

        # Create fresh Camoufox instance for each scrape
        camoufox = AsyncCamoufox(
            headless=headless,
            proxy=proxy,
            geoip=geoip,
        )

        # Start browser - this returns a Browser instance
        browser: Browser = await camoufox.start()

        try:
            # Create new page
            page: Page = await browser.new_page()

            # Block images, media, fonts, and stylesheets
            await page.route("**/*", lambda route: route.abort() 
                if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
                else route.continue_()
            )

            # Set viewport
            await page.set_viewport_size(
                viewport_size=ViewportSize(width=1920, height=1080)
            )

            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)

            # Navigate to URL
            logger.info(f"Navigating to {url}")
            try:
                await page.goto(url, timeout=timeout, wait_until="networkidle")
            except Exception as e:
                logger.warning(f"networkidle failed, trying domcontentloaded: {e}")
                await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)  # Wait 3 seconds after DOM loads

            # Wait for specific selector if provided
            if selector_to_wait_for:
                try:
                    await page.wait_for_selector(selector_to_wait_for, timeout=timeout)
                    logger.info(f"Found selector: {selector_to_wait_for}")
                except Exception as e:
                    logger.warning(f"Selector {selector_to_wait_for} not found: {e}")

            # Simulate human behavior
            await self._simulate_human_behavior(page)

            # Get final content
            content = await page.content()
            cookies_list = await page.context.cookies()
            cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
            
            logger.info(f"Retrieved {len(content)} chars from {url}. Cookies: {len(cookies_dict)}")

            return content, cookies_dict

        finally:
            # Always close browser
            await browser.close()

    async def _simulate_human_behavior(self, page: Page) -> None:
        """Simulate human-like behavior"""
        try:
            # Random delay before interacting
            await page.wait_for_timeout(random.randint(1000, 3000))

            # Random mouse movement
            await page.mouse.move(random.randint(100, 800), random.randint(100, 600))

            # Random scroll
            if random.random() < 0.7:
                await page.mouse.wheel(0, random.randint(-200, 200))
                await page.wait_for_timeout(random.randint(500, 1500))

        except Exception as e:
            logger.warning(f"Human behavior simulation failed: {e}")
