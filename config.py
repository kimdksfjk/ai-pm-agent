import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))

DATABASE_PATH = os.getenv("DATABASE_PATH", "agent_data.db")

MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "20"))
SUMMARY_THRESHOLD = int(os.getenv("SUMMARY_THRESHOLD", "10"))
