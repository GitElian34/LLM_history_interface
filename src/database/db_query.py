import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def get_all_items(article_id: int):
    """récupère tout les mots d'un article donné"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE article_id = ?", (article_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_numbers(article_id: int):
    """récupère uniquement les mots de type Number d'un article donné"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word FROM items WHERE type = 'Number' AND article_id = ?", (article_id,))
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows

def get_epoques(article_id: int):
    """récupère uniquement les mots de type Period d'un article donné"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT word FROM items WHERE type = 'Period' AND article_id = ?", (article_id,))
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


def search_etat_with_article_id(article_id: str):
    """
    Cherche un mot uniquement dans la table items.
    Retourne une liste des article_id où le mot est présent.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT etat FROM articles WHERE article_id = ?
    """, (article_id,))
    results = [row[0] for row in cur.fetchall()]

    conn.close()
    return results[0]

def search_word_in_db(word: str):
    """
    Cherche un mot uniquement dans la table items.
    Retourne une liste des article_id où le mot est présent.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT article_id FROM items WHERE word = ?
    """, (word,))
    results = [row[0] for row in cur.fetchall()]

    conn.close()
    return results


def get_all_articles():

    """Récupère tous les ids des articles présents dans la BDD"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT article_id FROM articles")
    rows = [row[0] for row in cur.fetchall()]
    conn.close()
    return rows



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

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"

def get_rappel(article_id: int, type_: str, method: str = "highlight"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tous les mots pertinents (pertinence ≠ Non ou NULL)
    cur.execute("""
        SELECT word FROM items
        WHERE article_id = ? AND type = ? AND (pertinence IS NOT NULL AND pertinence != 'Non')
    """, (article_id, type_))
    pertinents = set([row[0] for row in cur.fetchall()])

    if not pertinents:
        conn.close()
        return 0.0  # éviter division par zéro

    # Les mots trouvés par la méthode donnée
    if method:
        cur.execute("""
            SELECT word FROM items
            WHERE article_id = ? AND type = ? AND method = ?
        """, (article_id, type_, method))
    else:
        cur.execute("""
            SELECT word FROM items
            WHERE article_id = ? AND type = ?
        """, (article_id, type_))
    trouves = set([row[0] for row in cur.fetchall()])

    # Vrais positifs = intersection
    print(pertinents, trouves)
    vrais_positifs = pertinents & trouves

    rappel = len(vrais_positifs) / len(pertinents)
    conn.close()
    return rappel


def get_precision(article_id: int, type_: str, method: str = "highlight"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Les mots trouvés par la méthode donnée
    if method:
        cur.execute("""
            SELECT word, pertinence FROM items
            WHERE article_id = ? AND type = ? AND method = ?
        """, (article_id, type_, method))
    else:
        cur.execute("""
            SELECT word, pertinence FROM items
            WHERE article_id = ? AND type = ?
        """, (article_id, type_))

    rows = cur.fetchall()
    if not rows:
        conn.close()
        return 0.0

    total_trouves = len(rows)
    vrais_positifs = sum(1 for _, pertinence in rows if pertinence is not None and pertinence != "Non")

    precision = vrais_positifs / total_trouves
    conn.close()
    return precision

if __name__ == "__main__":
    print(get_all_articles())