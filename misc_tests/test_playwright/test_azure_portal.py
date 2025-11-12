import asyncio
from playwright.async_api import async_playwright, Browser, Page, Locator
import aiohttp
import tempfile
import subprocess
import os



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


async def playwright_iframe_example():
	
    await start_chrome_with_debug_port()
	

    playwright = await async_playwright().start()
	
    # Connect to an existing instance of Chrome using the connect_over_cdp method.
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")

    # Retrieve the first context of the browser.
    default_context = browser.contexts[0]

    # Retrieve the first page in the context.
    page = default_context.pages[0]
    
    #async with async_playwright() as playwright:
    # browser = await playwright.chromium.launch(headless=False)
    # page = await browser.new_page()
    
    await page.goto("https://portal.azure.com")
    
    # Method 1: frame_locator (recommended)
    iframe = page.frame_locator('iframe#_react_frame_0')

    # create_button = iframe.get_by_role('link', name='menuitem')
	
	
    create_button = iframe.locator('span.ms-Button-label', has_text="Create")

    count = await create_button.count()

    await create_button.click()
    
    # Method 2: Get frame by name
    frame = page.frame(name="BrowseResourceGroups.ReactView")
    if frame:
        await frame.locator('button').click()
    
    # Method 3: Get all frames
    for frame in page.frames:
        print(f"Frame: {frame.name} - {frame.url}")
        if "ResourceGroups" in frame.url:
            await frame.locator('text=Create').click()
            break
    
    await browser.close()


if __name__ == "__main__":
	


    print("\nExample 3: Working with iframes")
    asyncio.run(playwright_iframe_example())