import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def insert_item(word, type_, method):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO items (word, type, method)
        VALUES (?, ?, ?)
        """, (word, type_, method))
        conn.commit()
        print(f"Ajouté : {word} | {type_} | {method}")
    except sqlite3.IntegrityError:
        print(f"⚠ Entrée déjà existante : {word} avec la méthode {method}")

    conn.close()

if __name__ == "__main__":
    # Exemple d'ajout
    insert_item("chat", "animal", "analyse_textuelle")
    insert_item(42, "nombre", "traitement_numérique")
