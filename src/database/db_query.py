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


def get_numbers():
    """Récupère toutes les entités de type 'nombre'"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT word FROM items WHERE type = 'Number'")
    rows = [row[0] for row in cur.fetchall()]

    conn.close()
    return rows


def get_epoques():
    """Récupère toutes les entités de type 'epoque'"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT word FROM items WHERE type = 'Period'")
    rows = [row[0] for row in cur.fetchall()]

    conn.close()
    return rows


def get_entities():
    """Récupère toutes les entités PERSON, LOC et ORG"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT word, type FROM items WHERE type IN ('PERSON', 'LOC', 'ORG')")
    rows = cur.fetchall()

    conn.close()
    # Retourne un dict {type: [entités...]}
    entities = {"PERSON": [], "LOC": [], "ORG": []}
    for word, type_ in rows:
        entities[type_].append(word)

    return entities


if __name__ == "__main__":
    print("📋 Tous les items :", get_all_items())
    print("🔢 Nombres :", get_numbers())
    print("⏳ Époques :", get_epoques())
    print("🏷️ Entités :", get_entities())
