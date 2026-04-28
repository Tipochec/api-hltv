import os
from dotenv import load_dotenv
load_dotenv()

def get_url():
    API_KEY: str = os.getenv("API_KEY")
    BASE_URL = f"https://api.pandascore.co/csgo/matches?token={API_KEY}"
    return BASE_URL