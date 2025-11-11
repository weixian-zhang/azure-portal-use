import requests
import base64
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import base64
import os
load_dotenv()


base64_image = ''
path = os.path.join(os.path.dirname(__file__), 'az_portal_main.png')
with open(path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

llm = AzureChatOpenAI(
            deployment_name="gpt-4o",
            model="gpt-4o",
            api_version="2024-12-01-preview",
            temperature=0.0
        )

prompt = f"""Below base64 image is Azure Portal, name all HTML elements in this image.

image:
{base64_image}
"""
        
data_uri = f"data:image/png;base64,{base64_image}"

message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": """name all HTML elements in this image like buttons, textboxes, checkboxes, radio buttons, dropdowns, links and etc.

            If you see icons for Azure Services, include all their names as well.

            Also list all bounding boxes with their coordinates in format (x1, y1, x2, y2) where (x1, y1) is top-left corner and (x2, y2) is bottom-right corner.
            """
            
        },
        {
            "type": "image_url",
            "image_url": {"url": data_uri}
        }
    ]
)

response = llm.invoke([message])

print(response.content)
