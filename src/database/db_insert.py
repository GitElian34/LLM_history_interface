import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def insert_item(article_id, word, type_, method, pertinence=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM articles WHERE article_id = ?", (article_id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO articles (article_id) VALUES (?)", (article_id,))
        print(f"📄 Nouvel article ajouté : {article_id}")

    try:
        cur.execute("""
        INSERT INTO items (article_id, word, type, method, pertinence)
        VALUES (?, ?, ?, ?, ?)
        """, (article_id, word, type_, method, pertinence))
        conn.commit()
        print(f"✅ Ajouté : {word} | {type_} | {method} | pertinence={pertinence} | article={article_id}")
    except sqlite3.IntegrityError:
        print(f"⚠ Entrée déjà existante : {word} ({method}) dans article {article_id}")

    conn.close()

def update_pertinence(article_id, word, method, pertinence):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    UPDATE items
    SET pertinence = ?
    WHERE article_id = ? AND word = ? AND method = ?
    """, (pertinence, article_id, word, method))
    if cur.rowcount > 0:
        print(f"✅ Pertinence mise à jour pour {word} ({method}) dans article {article_id} → {pertinence}")
    else:
        print(f"⚠ Aucun item trouvé pour {word} ({method}) dans article {article_id}")
    conn.commit()
    conn.close()

# 🔥 Insérer/mettre à jour le texte d’une page
def insert_page_text(article_id, page_number, text):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM articles WHERE article_id = ?", (article_id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO articles (article_id) VALUES (?)", (article_id,))
        print(f"📄 Nouvel article ajouté : {article_id}")

    cur.execute("""
    INSERT INTO pages (article_id, page_number, text)
    VALUES (?, ?, ?)
    ON CONFLICT(article_id, page_number) DO UPDATE SET text = excluded.text
    """, (article_id, page_number, text))
    conn.commit()
    conn.close()
    print(f"✅ Texte enregistré pour article {article_id}, page {page_number}")

if __name__ == "__main__":
    insert_item(1, "chat", "animal", "analyse_textuelle", pertinence="moyenne")
    insert_page_text(1, 1, "Ceci est le texte de la page 1")
    insert_page_text(1, 2, "Ceci est le texte de la page 2")
