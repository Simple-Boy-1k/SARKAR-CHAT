import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
SUPPORT_CHAT_URL = os.getenv("SUPPORT_CHAT_URL", "")
SUPPORT_CHANNEL_URL = os.getenv("SUPPORT_CHANNEL_URL", "")
UPDATES_CHANNEL_URL = os.getenv("UPDATES_CHANNEL_URL", "")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://raw.githubusercontent.com/AashishTechs/Deep-Emotion/main/Welcome.jpg")
OUR_BOTS_URL = os.getenv("OUR_BOTS_URL", "")
