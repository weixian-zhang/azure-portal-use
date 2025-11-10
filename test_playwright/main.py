from playwright.sync_api import sync_playwright
from playwright.sync_api import Locator
from dotenv import load_dotenv
import os
import time
load_dotenv()

with sync_playwright() as p:
    # alternatively, connect over CDP
    # https://stackoverflow.com/questions/65802677/how-to-keep-browser-opening-by-the-end-of-the-code-running-with-playwright-pytho
    
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://portal.azure.com/", wait_until="domcontentloaded")

    username: Locator = page.locator('input[id="i0116"]')
    username.click()
    username.fill(os.getenv("username"))

    page.locator("#idSIButton9").click() # next button click

    password: Locator = page.locator('input[id="i0118"]')
    password.click()
    password.fill(os.getenv("password"))

    signin_btn = page.locator('#idSIButton9')
    signin_btn.click()

    #reduce number of signin prompt
    reduce_signin_no_btn = page.locator('#idBtn_Back')
    if reduce_signin_no_btn and reduce_signin_no_btn.is_visible():
        reduce_signin_no_btn.click()

    page.pause()

    # password: Locator = page.locator("#password").click()
    # password.fill(os.getenv("password"))

    # page.screenshot(path="example.png")
    #browser.close()


