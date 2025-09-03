import sqlite3
from pathlib import Path
import os

# Chemin de la base (dans le même dossier que ce fichier)
DB_PATH = Path(__file__).parent / "data.db"

def create_tables():
    """ Création de 3 tables :
    - La table articles, qui va contenir le nom des articles (ou leur numéro plutot) ainsi que l'état de complétion de ces derniers
    - La table items, qui va contenir pour chaque article tous les mots mis en avants de 5 types différents :
     Loc pour les lieux, Org pour les organismes  PER pour les personnes, Number pour les années et Period pour les périodes historiques
     accompagnés de leur méthode d'extraction (highlight par défaut) et de leur pertinence (initialisé à null et qui doit être
     modifié lors de l'utilisation de l'appli)
    - La table pages, qui va contenir les pages de l'article déja annoté afin de réduire le temps d'exécution et d'utilisation de l'appli
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Table articles (sans auto-increment, juste int)
    cur.execute("""
     CREATE TABLE IF NOT EXISTS articles (
         article_id INT PRIMARY KEY,
         etat TEXT
     )
     """)
    # Table des items (clé primaire composite : article_id + word + method)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
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