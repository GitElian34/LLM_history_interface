import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def insert_item(word, type_, method, pertinence=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO items (word, type, method, pertinence)
        VALUES (?, ?, ?, ?)
        """, (word, type_, method, pertinence))
        conn.commit()
        print(f"Ajouté : {word} | {type_} | {method} | pertinence={pertinence}")
    except sqlite3.IntegrityError:
        print(f"⚠ Entrée déjà existante : {word} avec la méthode {method}")

    conn.close()


def update_pertinence(word, method, pertinence):
    """Met à jour la pertinence d'un item identifié par (word, method)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    UPDATE items
    SET pertinence = ?
    WHERE word = ? AND method = ?
    """, (pertinence, word, method))

    if cur.rowcount > 0:
        print(f"✅ Pertinence mise à jour pour {word} ({method}) → {pertinence}")
    else:
        print(f"⚠ Aucun item trouvé pour {word} ({method})")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Exemple d'ajout
    insert_item("chat", "animal", "analyse_textuelle")
    insert_item("chien", "animal", "analyse_textuelle", pertinence="forte")

    # Exemple de mise à jour
    update_pertinence("chat", "analyse_textuelle", "faible")
    update_pertinence("chien", "analyse_textuelle", "très forte")
