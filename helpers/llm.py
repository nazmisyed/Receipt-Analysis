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
    Receipt_Date_Time: str
    Title: str
    Total_Amount: float
    File_Name: str
    Confidence: Literal["low", "medium", "high"]


INSTRUCTIONS = """
You extract receipt information from receipt images.
Return dates using ISO 8601 in MYT (UTC+08:00): YYYY-MM-DDTHH:MM:SS+08:00.
For Receipt_Date_Time, if the exact time is missing on receipt, use 00:00:00.
Keep Confidence as one of: low, medium, high.
"""


def _format_myt(value: datetime) -> str:
    return value.astimezone(MYT).strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + value.astimezone(MYT).strftime("%Y-%m-%dT%H:%M:%S%z")[-2:]


def _normalize_receipt_datetime(value: str) -> str:
    normalized = (value or "").strip().replace("Z", "+00:00")
    if not normalized:
        return _format_myt(datetime.now(tz=MYT))

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        # Fallback for date-only values from OCR/LLM output.
        try:
            parsed = datetime.strptime(normalized, "%Y-%m-%d").replace(tzinfo=MYT)
        except ValueError:
            return _format_myt(datetime.now(tz=MYT))

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=MYT)

    return _format_myt(parsed)


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
    output["Receipt_Date_Time"] = _normalize_receipt_datetime(output.get("Receipt_Date_Time", ""))
    output["Processed_Date_Time"] = _format_myt(datetime.now(tz=MYT))
    return output
