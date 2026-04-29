import sqlite3
import os
from utils.api import get_requests

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/example.db")
    return conn

def drop_tadles():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        DROP TABLE matchs
        '''
    )

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS matchs (
        id INTEGER PRIMARY KEY,
        team1 TEXT NULL,
        team2 TEXT NULL,
        logo1 TEXT NULL,
        logo2 TEXT NULL,
        score1 INTEGER NULL,
        score2 INTEGER NULL,
        status TEXT NULL,
        tournament TEXT NULL,
        date TEXT NULL
    )       
    '''
    )
    conn.commit()

def filling_table():
    matches = get_requests()
    conn = get_connection()
    cursor = conn.cursor()

    # Словарь перевода статусов
    status_map = {
        "finished": "Завершённые",
        "not_started": "Не начатые",
        "in_progress": "В процессе"
    }

    for match in matches:
        # Переводим статус перед записью
        translated_status = status_map.get(match['status'], match['status'])

        cursor.execute(
            '''
            INSERT OR REPLACE INTO matchs (
                id, team1, team2, logo1, logo2, score1, score2, status, tournament, date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                match['id'],
                match['team1'],
                match['team2'],
                match['logo1'],
                match['logo2'],
                match['score1'],
                match['score2'],
                translated_status,  # записываем уже переведённый статус
                match['tournament'],
                match['date'],
            )
        )

    conn.commit()
    conn.close()