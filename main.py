import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

API_KEY: str = os.getenv("API_KEY")
BASE_URL = f"https://api.pandascore.co/csgo/matches?token={API_KEY}"

response = requests.get(BASE_URL)
data = response.json()


for match in data:
    team1 = match["opponents"][0]["opponent"]["name"]
    team2 = match["opponents"][1]["opponent"]["name"]
    status = match["status"]
    score1 = match["results"][0]["score"]
    score2 = match["results"][1]["score"]
    tournament = match["league"]["name"]
    date = match["scheduled_at"]

    print(f"{team1} vs {team2} | {status} | {score1}:{score2} | {tournament} | {date}")

