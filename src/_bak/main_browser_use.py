from browser_use import Agent, ChatAzureOpenAI, BrowserSession, ActionResult, Tools, BrowserProfile
from playwright.async_api import Browser as PlaywrightBrowser, Page as PlaywrightPage
from chrome import start_chrome_with_debug_port, connect_playwright_to_cdp
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

base_url=os.getenv("AZURE_OPENAI_ENDPOINT")
model=os.getenv("OPENAI_MODEL_NAME")
openai_api_key=os.getenv("OPENAI_API_KEY")
username=os.getenv("AZURE_PORTAL_USERNAME")
password=os.getenv("AZURE_PORTAL_PASSWORD")
playwright_url = os.getenv("PLAYWRIGHT_URL")
playwright_browser: PlaywrightBrowser | None = None
playwright_page: PlaywrightPage | None = None

tools = Tools()

llm = ChatAzureOpenAI(
    model=model,
    api_version="2024-12-01-preview"
)



		# 3. after login, there will be multifactor authentication, you have to wait for a human to complete
		# 4. go to global search bar on the top, search for "resource groups", click the first search result to go to resource groups page.


@tools.action(description='find create menuitem button in iframe and click it')
async def find_click_create_menuitem(browser_session: BrowserSession, cdp_client):


    try:
        if not playwright_page:
            return ActionResult(error='Playwright not connected. Run setup first.')

        iframe_0 = playwright_page.frame_locator('iframe#_react_frame_0')

        # Handle special selectors
        # create_menuitem = iframe_0.get_by_role("menuitem", name="Create")
        create_button = iframe_0.locator('span.ms-Button-label', has_text="Create")

        count = await create_button.count()
        if count != 1:
            return ActionResult(error='Create menuitem not found or multiple found.')
        # if not create_menuitem:
        #     return ActionResult(extracted_content='No Create button found')

        await create_button.click()

        return ActionResult(
            extracted_content='Tool clicked Create button',
        )

    except Exception as e:
        error_msg = f'❌ Playwright text extraction failed: {str(e)}'
        return ActionResult(error=error_msg)
 

async def main():

    global playwright_browser, playwright_page


    chrome_process = await start_chrome_with_debug_port()

    playwright_browser, playwright_page = await connect_playwright_to_cdp(playwright_url)


    browser_session = BrowserSession(cdp_url=playwright_url, 
                                     browser_profile=BrowserProfile(
                                         window_size={'width': 1920, 'height': 1080},
                                         headless=False,
                                         user_data_dir=None,
                                         disable_security=True))


    
    #if you cannot find element, do not try to find it yourself, use tools provided.

    # to find and click Create button, use tool: find_click_Create_button
    agent = Agent(
        task=f"""
            You are an AI agent that can automate Azure resource management tasks in Azure portal itself as human doing browser tasks.

            

            <instructions>
            1. go to Azure Portal https://portal.azure.com
            
            2. you will be asked to login.
            if you see username Weixian Admin, click on button, otherwise enter the username {username} and click next.
            
            3. go to global search bar on the top, search for "resource group", select "Resource Groups".

            4. find and click "Create" menuitem button, this will open create resource group panel.
            
            5. select Subscription dropdown: select "Weixian-1"
            
            6. Resource group name: fill in "rg-create-by-agent"
            
            7. click "Review + create" button on the bottom.
            
            8. click "Create" button.
            
            9. task complete
            
            </instructions>

            <login credentials>
            username:{username}
            password:{password}
            </login credentials>
        """,
        llm=llm,
        browser_session=browser_session,
        #tools=tools
    )

    #playwright_browser, playwright_page = await connect_playwright_to_cdp(playwright_url)

    await agent.run()



if __name__ == "__main__":
    asyncio.run(main())
