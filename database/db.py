import sqlite3
import os
from utils.api import get_requests

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/example.db")
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS matchs (
        id INTEGER PRIMARY KEY,
        team1 TEXT NULL,
        team2 TEXT NULL,
        score1 INTEGER NOT NULL,
        score2 INTEGER NOT NULL,
        status TEXT NOT NULL,
        tournament TEXT NOT NULL,
        date TEXT NOT NULL
    )       
    '''
    )
    conn.commit()

def filling_table():
    matches = get_requests()
    conn = get_connection()
    cursor = conn.cursor()
    for match in matches:
        cursor.execute(
        '''
        INSERT OR REPLACE INTO matchs (id, team1, team2, score1, score2, status, tournament, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match['id'], match['team1'], match['team2'], match['score1'] ,match['score2'], match['status'], match['tournament'],match['date'],)
        )
    conn.commit()
    conn.close()