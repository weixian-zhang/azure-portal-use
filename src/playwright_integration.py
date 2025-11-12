from playwright.async_api import Browser, Page, async_playwright
from typing import Tuple
import tempfile
import asyncio
import subprocess
import os
import aiohttp

async def start_chrome_with_debug_port(port: int = 9222):
	"""
	Start Chrome with remote debugging enabled.
	Returns the Chrome process.
	"""
	# Create temporary directory for Chrome user data
	user_data_dir = tempfile.mkdtemp(prefix='chrome_cdp_')

	# Chrome launch command
	chrome_paths = [
		'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
		'/usr/bin/google-chrome',  # Linux
		'/usr/bin/chromium-browser',  # Linux Chromium
		'chrome',  # Windows/PATH
		'chromium',  # Generic
	]

	chrome_exe = None
	for path in chrome_paths:
		if os.path.exists(path) or path in ['chrome', 'chromium']:
			try:
				# Test if executable works
				test_proc = await asyncio.create_subprocess_exec(
					path, '--version', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
				)
				await test_proc.wait()
				chrome_exe = path
				break
			except Exception:
				continue

	if not chrome_exe:
		raise RuntimeError('❌ Chrome not found. Please install Chrome or Chromium.')

	# Chrome command arguments
	cmd = [
		chrome_exe,
		f'--remote-debugging-port={port}',
		f'--user-data-dir={user_data_dir}',
		'--no-first-run',
		'--no-default-browser-check',
		'--disable-extensions',
		'about:blank',  # Start with blank page
	]

	# Start Chrome process
	process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	# Wait for Chrome to start and CDP to be ready
	cdp_ready = False
	for _ in range(20):  # 20 second timeout
		try:
			async with aiohttp.ClientSession() as session:
				async with session.get(
					f'http://localhost:{port}/json/version', timeout=aiohttp.ClientTimeout(total=1)
				) as response:
					if response.status == 200:
						cdp_ready = True
						break
		except Exception:
			pass
		await asyncio.sleep(1)

	if not cdp_ready:
		process.terminate()
		raise RuntimeError('❌ Chrome failed to start with CDP')

	return process
	
async def connect_playwright_to_cdp(cdp_url: str) -> Tuple[Browser | None, Page | None]:
	"""
	Connect Playwright to the same Chrome instance Browser-Use is using.
	This enables custom actions to use Playwright functions.
	"""

	playwright = await async_playwright().start()
	playwright_browser = await playwright.chromium.connect_over_cdp(cdp_url)

	# Get or create a page
	if playwright_browser and playwright_browser.contexts and playwright_browser.contexts[0].pages:
		playwright_page = playwright_browser.contexts[0].pages[0]
	elif playwright_browser:
		context = await playwright_browser.new_context()
		playwright_page = await context.new_page()

	return playwright_browser, playwright_page
