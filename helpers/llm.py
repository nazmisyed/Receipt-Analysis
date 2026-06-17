import base64
import os
from datetime import datetime, timezone
from typing import Literal

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIResponsesModel ,OpenAIChatModelSettings

from pydantic_ai.providers.openai import OpenAIProvider

from pydantic import BaseModel

from config import OPEN_AI_ENDPOINT, OPEN_AI_KEY, OPEN_AI_DEPLOYMENT_NAME



class ReceiptExtraction(BaseModel):
    Receipt_Date_Time: str
    Title: str
    Total_Amount: str
    File_Name: str
    Confidence: Literal["low", "medium", "high"]


INSTRUCTIONS = """
You are an AI agent that extracts receipt information from text.
"""


def get_azureopenai_model() -> AsyncAzureOpenAI:
    client = AsyncAzureOpenAI(
        azure_endpoint=OPEN_AI_ENDPOINT,
        api_key=OPEN_AI_KEY,
    )
    model = OpenAIResponsesModel(
        OPEN_AI_DEPLOYMENT_NAME,
        provider=OpenAIProvider(openai_client=client),
    )
    return model

def get_model_settings() -> OpenAIChatModelSettings:
    return OpenAIChatModelSettings(
        temperature=0.2,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )


async def extract_receipt_info(img_data) -> ReceiptExtraction:
    model = get_azureopenai_model()
    settings = get_model_settings()
    agent = Agent(
        model=model,
        instructions=INSTRUCTIONS,
        output_type=ReceiptExtraction,
        model_settings=settings,
    )
    image_input = [BinaryContent(data=img_data, media_type="image/jpeg") ]
    response = await agent.run(user_prompt=image_input)
    output = response.model_dump(mode="json")
    output["Processed_Date_Time"] = datetime.now(timezone.utc).isoformat()
    return output
