import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is missing in the .env file.")

settings = Settings()