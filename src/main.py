from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain_core.tools import Tool
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from chrome import start_chrome_with_debug_port
from playwright_integration import PlaywrightManager
from pydantic import BaseModel, Field
import asyncio
import os


class AgentResult(BaseModel):
    thinking: str = Field(..., description="A structured <think>-style reasoning block that applies the <reasoning_rules> provided above.")
    evaluation_previous_goal: str = Field(..., description="Concise one-sentence analysis of your last action. Clearly state success, failure, or uncertain.")
    memory: str = Field(..., description="1-3 sentences of specific memory of this step and overall progress. You should put here everything that will help you track progress in future steps. Like counting pages visited, items found, etc.")
    next_goal: str = Field(..., description="State the next immediate goal and action to achieve it, in one clear sentence.")
    action: str = Field(..., description="Use tools to perform webpage actions like click button, fill textboxes, click dropdown and more. or put 'None' if no further actions need to be performed as task is completed.")


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

playwright_manager = PlaywrightManager()

cdp_url = 'http://127.0.0.1:9222'
agent_history = []
#excluded_tools = ['performance_analyze_insight', 'performance_start_trace', 'performance_stop_trace']  # List of tool names to exclude
# exclude playwright tools that uses accessibility.snapshot refid to find element
excluded_tools = ['browser_snapshot', 'browser_click', 'browser_drag']  # List of tool names to exclude
image_url = f"data:image/png;base64,{base64_image}"
chrome_browser = None
webpage = None


def browser_get_page_html():
    frames_html = asyncio.run(playwright_manager.get_all_iframe_dom())


def structued_output_parser(response_content: str) -> AgentResult:
    # get string after ``json in response.content
    json_str = response_content.split("```json")[1].split("```")[0]
    result = AgentResult.model_validate_json(json_str)
    return result


async def main():
    

    try:

        await start_chrome_with_debug_port()

        await playwright_manager.connect_playwright_to_cdp()

        # await playwright_manager.snapshot_accessibility_tree_for_all_iframes()

        
        client = MultiServerMCPClient(  
            {
                "playwright": {
                    "transport": "stdio",  # Local subprocess communication
                    "command": "npx",
                    # Absolute path to your math_server.py file
                    "args": [f"@playwright/mcp@latest"],
                }
            }
            # {
            #     "chrome-devtools-mcp": {
            #         "transport": "stdio",  # Local subprocess communication
            #         "command": "npx",
            #         # Absolute path to your math_server.py file
            #         "args": ["chrome-devtools-mcp@latest"],
            #     }
            # }
        )

        tools = await client.get_tools()
        tools = [t for t in tools if t.name not in excluded_tools]

        llm = AzureChatOpenAI(
                    deployment_name="gpt-4o",
                    model="gpt-4o",
                    api_version="2024-12-01-preview",
                    temperature=0.0
                ).bind_tools(tools)

        

        frames_html = await playwright_manager.get_all_iframe_dom()

        for i in range(1, len(frames_html)):

            user_prompt = user_prompt_template.format(
                user_request="""
                find the Create button with plus sign "+ Create" and click it
                """,
                webpage_html=frames_html[i])
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content= [
                    {"type": "text", "text": user_prompt}
                    #{"type": "image_url", "image_url": {"url": image_url}},
                ])
            ]

            response: AIMessage = llm.invoke(input=messages)

            agent_output: AgentResult = structued_output_parser(response.content)

            pass

    except Exception as e:
        print(f"❌ An error occurred: {e}")


    # beatifulsoup to reduce html size
    # https://stackoverflow.com/questions/76847648/reducing-dom-html-size-in-client-side-using-beautifulsoup

    # playwright_connected = await playwright.connect_playwright_to_cdp()

    # all_frame_axtrees = await playwright.snapshot_accessibility_tree_for_all_iframes()

    # cwd = os.path.dirname(os.path.abspath(__file__))
    # yaml.dump(all_frame_axtrees, open(os.path.join(cwd, 'all_frame_axtrees.yaml'), 'w'))
    
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
