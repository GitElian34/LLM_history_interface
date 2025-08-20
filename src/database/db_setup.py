import sqlite3
from pathlib import Path
import os

# Chemin de la base (dans le même dossier que ce fichier)
DB_PATH = Path(__file__).parent / "data.db"

def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Table articles (sans auto-increment, juste int)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        article_id INT PRIMARY KEY
    )
    """)

    # Table des items (clé primaire composite : article_id + word + method)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS item8s (
        article_id INTEGER NOT NULL,
        word TEXT NOT NULL,
        type TEXT NOT NULL,
        method TEXT NOT NULL,
        pertinence TEXT,
        PRIMARY KEY (article_id, word, method),
        FOREIGN KEY (article_id) REFERENCES articles(article_id)
    )
    """)

    # 🔥 Nouvelle table pour stocker le texte par page
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        article_id INTEGER NOT NULL,
        page_number TEXT NOT NULL,
        text TEXT,
        PRIMARY KEY (article_id, page_number),
        FOREIGN KEY (article_id) REFERENCES articles(article_id)
    )
    """)

    conn.commit()
    conn.close()

def reset_database():
    """Supprime la base et recrée les tables vides."""
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print("💥 Base de données supprimée.")

    create_tables()
    print("✅ Nouvelles tables (articles + items + pages) initialisées.")

if __name__ == "__main__":
    reset_database()