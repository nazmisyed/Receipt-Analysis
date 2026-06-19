from datetime import datetime, timedelta, timezone
from typing import Literal

from openai import AsyncOpenAI
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIChatModelSettings

from pydantic_ai.providers.openai import OpenAIProvider

from pydantic import BaseModel

from config import  OPEN_AI_ENDPOINT, OPEN_AI_KEY, OPEN_AI_DEPLOYMENT_NAME


MYT = timezone(timedelta(hours=8), name="MYT")



class ReceiptExtraction(BaseModel):
    Receipt_Date: str
    Title: str
    Total_Amount: float
    Confidence: Literal["low", "medium", "high"]


INSTRUCTIONS = """
You are an expert data extraction assistant. Your task is to accurately extract structured information from receipt images.

Strictly adhere to the following rules for each field:

1. Receipt_Date: These receipts are from Malaysia. You MUST assume any ambiguous dates printed on the receipt follow the DD/MM/YYYY (Day-Month-Year) format. Extract the date and convert it to be formatted STRICTLY as YYYY-MM-DD (e.g., "2024-06-18"). Do NOT include the time. If missing, use "Unknown".
2. Title: Extract the primary Vendor, Merchant, or Store Name. Do not include branch locations unless part of the main name. If completely unreadable, output "Unknown".
3. Total_Amount: Extract the FINAL total amount paid. Do not extract the subtotal or tax amounts. Return only the numeric value. Do NOT include currency symbols (e.g., return 31.00, not $31.00).
4. Confidence: Assess the legibility of the receipt. 
   - Use "high" if all extracted fields are clearly visible.
   - Use "medium" if the image is blurry but readable.
   - Use "low" if critical information is cut off, heavily distorted, or guessed.
"""


def _format_date(value: datetime) -> str:
    return value.astimezone(MYT).strftime("%Y-%m-%d")


def _normalize_receipt_date(value: str) -> str:
    normalized = (value or "").strip().replace("Z", "+00:00")
    if not normalized:
        return _format_date(datetime.now(tz=MYT))

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        # Fallback for date-only values from OCR/LLM output.
        try:
            parsed = datetime.strptime(normalized, "%Y-%m-%d").replace(tzinfo=MYT)
        except ValueError:
            return _format_date(datetime.now(tz=MYT))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=MYT)

    return _format_date(parsed)


def get_azureopenai_model() -> OpenAIResponsesModel:
    client = AsyncOpenAI(
        base_url=OPEN_AI_ENDPOINT,
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


async def extract_receipt_info(img_data: bytes, media_type: str = "image/jpeg") -> ReceiptExtraction:
    model = get_azureopenai_model()
    settings = get_model_settings()
    agent = Agent(
        model=model,
        instructions=INSTRUCTIONS,
        output_type=ReceiptExtraction,
        model_settings=settings,
    )
    image_input = [BinaryContent(data=img_data, media_type=media_type)]
    response = await agent.run(user_prompt=image_input)
    output = response.output.model_dump(mode="json")
    output["Receipt_Date"] = _normalize_receipt_date(output.get("Receipt_Date", ""))
    output["Processed_Date_Time"] = _format_date(datetime.now(tz=MYT))
    return output
