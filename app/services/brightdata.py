import asyncio
import logging
import random
import time
from typing import Optional
from playwright.async_api import Playwright, async_playwright, ViewportSize  # type: ignore[import-not-found]
from app.config import settings
from app.models import ScrapeResponse, ScraperType
from app.services.base import BaseScraper

logger = logging.getLogger(__name__)


class BrightDataCDPScraper(BaseScraper):
    def __init__(self) -> None:
        self.playwright: Optional[Playwright] = None
        self.cdp_endpoint = settings.BRIGHTDATA_CDP_ENDPOINT

    @property
    def name(self) -> ScraperType:
        return ScraperType.BRIGHTDATA_CDP

    async def initialize(self) -> None:
        self.playwright = await async_playwright().start()
        logger.info("BrightData CDP scraper initialized")

    async def cleanup(self) -> None:
        """Cleans up Playwright resources"""
        if self.playwright:
            await self.playwright.stop()
            logger.info("BrightData CDP scraper stopped")
            self.playwright = None

    async def scrape(
        self,
        url: str,
        selector_to_wait_for: Optional[str] = None,
        timeout: int = 30000,
        headless: bool = True,
        max_retries: int = 3,
        **kwargs,
    ) -> ScrapeResponse:
        start_time = time.time()
        retries = 0

        for attempt in range(max_retries + 1):
            try:
                content = await self._scrape_with_brightdata_cdp(
                    url, selector_to_wait_for, timeout, headless
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
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue

                return ScrapeResponse(
                    success=True,
                    html=content,
                    content_length=content_length,
                    execution_time=execution_time,
                    scraper_used=self.name,
                    retries_attempted=retries,
                )

            except Exception as e:
                logger.error(
                    f"BrightData scrape attempt {attempt + 1} failed for {url}: {e}"
                )
                retries += 1

                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                else:
                    execution_time = time.time() - start_time
                    return ScrapeResponse(
                        success=False,
                        error=str(e),
                        execution_time=execution_time,
                        scraper_used=self.name,
                        retries_attempted=retries,
                    )

        # This shouldn't be reached, but just in case
        execution_time = time.time() - start_time
        return ScrapeResponse(
            success=False,
            error="Max retries exceeded",
            execution_time=execution_time,
            scraper_used=self.name,
            retries_attempted=retries,
        )

    async def _scrape_with_brightdata_cdp(
        self,
        url: str,
        selector_to_wait_for: Optional[str] = None,
        timeout: int = 30000,
        headless: bool = True,
    ) -> str:
        if not self.playwright:
            raise ValueError("Playwright not initialized")

        browser = await self.playwright.chromium.connect_over_cdp(self.cdp_endpoint)

        try:
            page = await browser.new_page()

            viewport_sizes = [
                {"width": 1920, "height": 1080},  # Full HD
                {"width": 1366, "height": 768},  # Laptop
                {"width": 1440, "height": 900},  # MacBook
                {"width": 1536, "height": 864},  # Windows laptop
                {"width": 1280, "height": 720},  # HD
                {"width": 1600, "height": 900},  # HD+
            ]

            viewport = random.choice(viewport_sizes)
            await page.set_viewport_size(
                viewport_size=ViewportSize(
                    width=viewport["width"], height=viewport["height"]
                )
            )
            logger.debug(
                f"Set viewport size to viewport: {viewport['width']}x{viewport['height']}"
            )

            random_delay = random.uniform(8.0, 25.0)
            logger.debug(
                f"Waiting for {random_delay} seconds before navigating to {url}"
            )
            await page.wait_for_timeout(random_delay * 1000)

            logger.info(f"Navigating to {url}")
            await page.goto(url, timeout=timeout, wait_until="networkidle")
            await page.wait_for_timeout(5000)

            if selector_to_wait_for:
                logger.info(f"Waiting for selector: {selector_to_wait_for}")
                await page.wait_for_selector(selector_to_wait_for, timeout=timeout)

            await page.wait_for_timeout(2000)

            await self._simulate_human_behavior(page, viewport)

            logger.info("Waiting for page to stabilize...")
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                logger.error("Network idle timeout - continuing anyway")

            await page.wait_for_timeout(3000)

            content = await page.content()

            # Handle anti-bot challenges
            if "chlgeId" in content or "challenge" in content.lower():
                logger.info(f"Anti-bot challenge detected for {url}")
                content = await self._handle_challenge(page)

            content_length = len(content)
            logger.info(f"✅ Content length: {content_length} characters")

            return content

        finally:
            await browser.close()
            logger.info("✅ Browser closed")

    async def _simulate_human_behavior(self, page, viewport):
        """Simulate human-like mouse movements and scrolling"""
        try:
            # Your existing human behavior simulation logic
            start_x, start_y = 400, 300
            num_points = random.randint(4, 8)
            points = []
            current_x, current_y = start_x, start_y

            for i in range(num_points):
                if i == 0:
                    x = current_x + random.randint(-100, 100)
                    y = current_y + random.randint(-80, 80)
                else:
                    max_jump = min(150, viewport["width"] // 6)
                    x = current_x + random.randint(-max_jump, max_jump)
                    y = current_y + random.randint(-max_jump, max_jump)

                x = max(50, min(viewport["width"] - 50, x))
                y = max(50, min(viewport["height"] - 50, y))
                points.append((x, y))
                current_x, current_y = x, y

            # Move through waypoints with realistic timing
            for i, (x, y) in enumerate(points):
                if i > 0:
                    prev_x, prev_y = points[i - 1]
                    distance = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5
                    speed = random.uniform(300, 700)
                    move_time = distance / speed * random.uniform(0.8, 1.2)
                else:
                    move_time = random.uniform(0.1, 0.3)

                await page.mouse.move(x, y)
                await page.wait_for_timeout(move_time * 1000)

                if random.random() < 0.3:
                    pause_time = random.uniform(0.2, 0.8)
                    await page.wait_for_timeout(pause_time * 1000)

            # Realistic scrolling
            if random.random() < 0.7:  # 70% chance to scroll
                await page.mouse.wheel(0, random.randint(-200, 200))
                await page.wait_for_timeout(random.uniform(200, 500))

            natural_pause = random.uniform(800, 2500)
            await page.wait_for_timeout(natural_pause)

        except Exception as e:
            logger.warning(f"Human behavior simulation failed: {e}")

    async def _handle_challenge(self, page):
        """Handle anti-bot challenges using staged waiting strategy"""
        logger.info("Using staged waiting strategy to resolve challenge...")

        for stage in range(3):
            logger.info(f"Challenge resolution stage {stage + 1}/3...")
            await page.wait_for_timeout(8000)

            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                logger.info("Page still loading...")

            content = await page.content()

            challenge_gone = (
                "chlgeId" not in content and "challenge" not in content.lower()
            )
            title_element_found = False

            try:
                title_element = await page.query_selector("h1.bfsTitle")
                title_element_found = title_element is not None
                if title_element_found:
                    logger.info("✅ Found h1.bfsTitle - page appears fully loaded!")
            except Exception:
                pass

            if challenge_gone or title_element_found:
                logger.info("✅ Challenge resolved!")
                break
            else:
                logger.info(f"Challenge still active after stage {stage + 1}")

        return await page.content()
