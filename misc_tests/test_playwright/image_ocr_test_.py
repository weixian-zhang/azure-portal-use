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
path = os.path.join(os.path.dirname(__file__), 'resource_group_page.png')
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

create_btn_alert = f"""
image is a screenshot of Azure Portal website.

locate the Create button with. plus sign in the image whetehr is it visible or not.

If visible, return the estimated javascript mouse cursor X Y coordinates in the image.
"""

message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": """
            image is a screenshot of Azure Portal website.

            locate table row object with name "DefaultResourceGroup-CCAN" in the image whether is it visible or not.

            If visible, return the estimated javascript mouse cursor X Y coordinates in the image.
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
