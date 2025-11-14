from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from chrome import start_chrome_with_debug_port
from playwright_integration import connect_playwright_to_cdp
import asyncio
import os
import json

system_prompt = ''
user_prompt_template = ''
base64_image = ''
cwd = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(cwd, 'system_prompt.md'), 'r') as f:
    system_prompt = f.read()
with open(os.path.join(cwd, 'user_prompt.md'), 'r') as f:
    user_prompt_template = f.read()
with open(os.path.join(cwd, 'base64_image.txt'), 'r') as f:
    base64_image = f.read()


async def test_playwright_connection():
    cdp_url = 'http://127.0.0.1:9222'
    browser, page = await connect_playwright_to_cdp(cdp_url)
    if browser and page:
        print("Connected to Chrome via Playwright.")
        await page.goto('https://portal.azure.com')


agent_history = []
excluded_tools = ['performance_analyze_insight', 'performance_start_trace', 'performance_stop_trace']  # List of tool names to exclude

image_url = f"data:image/png;base64,{base64_image}"


async def main():

    await start_chrome_with_debug_port()

    await test_playwright_connection()

    llm = AzureChatOpenAI(
                deployment_name="gpt-4o",
                model="gpt-4o",
                api_version="2024-12-01-preview",
                temperature=0.0
            )

    client = MultiServerMCPClient(  
        {
            "chrome-devtools-mcp": {
                "transport": "stdio",  # Local subprocess communication
                "command": "npx",
                # Absolute path to your math_server.py file
                "args": ["chrome-devtools-mcp@latest"],
            }
        }
    )

    tools = await client.get_tools()
    tools = [t for t in tools if t.name not in excluded_tools]

    llm.bind_tools(tools)

    for t in tools:
        if t.name == 'take_snapshot':
            result = t.invoke(input= '', verbose= True)
            break


    # input('Press Enter after Chrome has started...')

    # user_prompt = user_prompt_template.format(agent_history=json.dumps(agent_history), user_request="""
    # find the Create button with plus sign "+ Create" and click it
    # """)

    # messages = [
    #     SystemMessage(content=system_prompt),
    #     HumanMessage(content= [
    #     {"type": "text", "text": user_prompt}
    #     #{"type": "image_url", "image_url": {"url": image_url}},
    # ])]


    # response: AIMessage = llm.invoke(input=messages)

    # # get string after ``json in response.content
    # json_str = response.content.split("```json")[1].split("```")[0]

    # agent_history.append(json.loads(json_str))

    # steps = 10

    # while steps > 0:

    #     user_prompt = user_prompt_template.format(agent_history=agent_history[0]['action'], user_request="""
    #     find the Create button with plus sign "+ Create" and click it
    #     """)

    #     tools[0].invoke

    #     response: AIMessage = llm.invoke(input=messages)

    #     steps -= 1


asyncio.run(main())
