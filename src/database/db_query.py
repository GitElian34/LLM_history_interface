import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def get_all_items():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT * FROM items")
    rows = cur.fetchall()

    conn.close()
    return rows

if __name__ == "__main__":
    data = get_all_items()
    for row in data:
        print(row)
