from config import get_url
import requests

BASE_URL = get_url()

def get_requests():
    response = requests.get(BASE_URL)
    data = response.json()
    list = []
    print(data)
    print(list)
    for match in data:
        
        if len(match['opponents']) < 2:
            continue
        id = match['id']
        team1 = match["opponents"][0]["opponent"]["name"]
        team2 = match["opponents"][1]["opponent"]["name"]
        status = match["status"]
        score1 = match["results"][0]["score"]
        score2 = match["results"][1]["score"]
        tournament = match["league"]["name"]
        date = match["scheduled_at"]
    
        list.append({
            'id': id,
            'team1': team1,
            'team2': team2,
            'status': status,
            'score1': score1,
            'score2': score2,
            'tournament': tournament,
            'date': date
        })
        print(list)
    return list

