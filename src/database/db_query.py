import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def get_all_items(article_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE article_id = ?", (article_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_numbers(article_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word FROM items WHERE type = 'Number' AND article_id = ?", (article_id,))
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows

def get_epoques(article_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word FROM items WHERE type = 'Period' AND article_id = ?", (article_id,))
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows

def get_all_articles():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT article_id FROM articles")
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows

def get_entities(article_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT word, type FROM items 
        WHERE type IN ('PERSON', 'LOC', 'ORG') AND article_id = ?
    """, (article_id,))
    rows = cur.fetchall()
    conn.close()
    entities = {"PERSON": [], "LOC": [], "ORG": []}
    for word, type_ in rows:
        entities[type_].append(word)
    return entities

# 🔥 Récupérer le texte d’une page spécifique
def get_page_text(article_id: int, page_number: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT text FROM pages WHERE article_id = ? AND page_number = ?", (article_id, page_number))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# 🔥 Récupérer toutes les pages d’un article
def get_article_pages(article_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT page_number, text FROM pages WHERE article_id = ? ORDER BY page_number", (article_id,))
    rows = cur.fetchall()
    conn.close()
    return {page: text for page, text in rows}

if __name__ == "__main__":
    print(get_all_articles())