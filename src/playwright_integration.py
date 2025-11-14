from playwright.async_api import Browser, Page, async_playwright
from typing import Tuple

async def connect_playwright_to_cdp(cdp_url: str) -> Tuple[Browser | None, Page | None]:
	"""
	Connect Playwright to the same Chrome instance Browser-Use is using.
	This enables custom actions to use Playwright functions.
	"""

	try:
		playwright = await async_playwright().start()
		playwright_browser = await playwright.chromium.connect_over_cdp(cdp_url)

		# Get or create a page
		if playwright_browser and playwright_browser.contexts and playwright_browser.contexts[0].pages:
			playwright_page = playwright_browser.contexts[0].pages[0]
		elif playwright_browser:
			context = await playwright_browser.new_context()
			playwright_page = await context.new_page()

	

		return playwright_browser, playwright_page
	except Exception as e:
		print(f"❌ Failed to connect Playwright to CDP: {e}")
		return None, None
	

