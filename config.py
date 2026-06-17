from dotenv import load_dotenv
import os

load_dotenv()

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
OPEN_AI_ENDPOINT = os.getenv("OPEN_AI_ENDPOINT")
OPEN_AI_DEPLOYMENT_NAME = os.getenv("OPEN_AI_DEPLOYMENT_NAME")

