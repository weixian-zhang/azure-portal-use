from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_openai import AzureChatOpenAI
from chrome import start_chrome_with_debug_port, connect_playwright_to_cdp
import asyncio


excluded_tools = ['performance_analyze_insight', 'performance_start_trace', ''performance_stop_trace'']  # List of tool names to exclude

async def main():

    await start_chrome_with_debug_port()


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

    client.session("chrome-devtools-mcp")

    input('Press Enter after Chrome has started...')

    tools = await client.get_tools()

    tools = [t for t in tools if t.name not in excluded_tools]

    llm.bind_tools(tools)

    steps = 10

    while steps > 0:

        steps -= 1


asyncio.run(main())
