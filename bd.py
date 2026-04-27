import sqlite3

conn = sqlite3.connect("example.db")
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS match (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1 TEXT NOT NULL,
        team2 TEXT NOT NULL,
        score1 INTEGER NOT NULL,
        score2 INTEGER NOT NULL,
        status TEXT NOT NULL,
        tournament TEXT NOT NULL,
        date TEXT NOT NULL
    )       
    '''
    )

conn.commit()
conn.close()