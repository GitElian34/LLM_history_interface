import sqlite3
from pathlib import Path
import os

# Chemin de la base (dans le même dossier que ce fichier)
DB_PATH = Path(__file__).parent / "data.db"

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        word TEXT NOT NULL,
        type TEXT NOT NULL,
        method TEXT NOT NULL,
        PRIMARY KEY (word, method)
    )
    """)

    conn.commit()
    conn.close()

def reset_database():
    """Supprime la base et recrée la table vide."""
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print("💥 Base de données supprimée.")

    create_table()
    print("✅ Nouvelle base de données initialisée.")

if __name__ == "__main__":
    # Exemple d'utilisation
    # create_table()       # Juste créer si elle n'existe pas
    reset_database()       # Supprimer et recréer
