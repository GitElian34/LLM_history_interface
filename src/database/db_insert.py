import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def insert_item(article_id, word, type_, method, pertinence=None):
    """Permet d'insérer un triplé mot, type du mot et méthode d'extraction dans la table items (créer également l'article s'il n'existe pas)"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM articles WHERE article_id = ?", (article_id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO articles (article_id,etat) VALUES (?,?)", (article_id,"Non complété"))
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
    """Permet de mettre à jour la pertinence d'une entité en particulier (un mot) réserver à l'usage de l'historien"""
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

def update_etat(article_id: int, etat: str):
    """Met à jour ou insère l'état d'un article."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("9")
    # Vérifie si l'article existe
    cur.execute("SELECT 1 FROM articles WHERE article_id = ?", (article_id,))
    if cur.fetchone() is None:
        # Insère un nouvel article avec son état
        cur.execute("INSERT INTO articles (article_id, etat) VALUES (?, ?)", (article_id, etat))
        print(f"📄 Nouvel article ajouté {article_id} avec état='{etat}'")
    else:
        # Met à jour l’état
        cur.execute("UPDATE articles SET etat = ? WHERE article_id = ?", (etat, article_id))
        print(f"🔄 État mis à jour pour article {article_id} → {etat}")

    conn.commit()
    conn.close()

# 🔥 Insérer/mettre à jour le texte d’une page
def insert_pages_dict(article_id, pages_dict: dict):
    """
    Insère ou met à jour toutes les pages d'un article à partir d'un dictionnaire.

    Args:
        article_id (int): ID de l'article.
        pages_dict (dict): Dictionnaire contenant tout le texte de l'article annoté {page_number: texte}
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Vérifier si l'article existe
    cur.execute("SELECT 1 FROM articles WHERE article_id = ?", (article_id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO articles (article_id) VALUES (?)", (article_id,))
        print(f"📄 Nouvel article ajouté : {article_id}")

    # Insérer chaque page du dictionnaire
    for page_number, text in pages_dict.items():
        cur.execute("""
        INSERT INTO pages (article_id, page_number, text)
        VALUES (?, ?, ?)
        ON CONFLICT(article_id, page_number) DO UPDATE SET text = excluded.text
        """, (article_id, page_number, text))
        print(f"✅ Texte enregistré pour article {article_id}, page {page_number}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_item(1, "chat", "animal", "analyse_textuelle", pertinence="moyenne")
