from collections import defaultdict

import pyautogui
import time
import webbrowser
from netscraping import *
# Ouvre l'article dans ton navigateur par défaut



def extract_key_from_url(url: str) -> str:
    """
    Extrait la clé 'année-numéro' ou 'année-hos' depuis l'URL d'un article Persee.
    Exemple :
      https://www.persee.fr/doc/medio_0223-3843_1979_num_2_1_1637 -> "1979-2"
      https://www.persee.fr/doc/medio_0223-3843_1990_hos_1_1       -> "1990-hos"
    """
    # Cas spécial : "hos"
    match_hos = re.search(r"(\d{4})_hos", url)
    if match_hos:
        return f"{match_hos.group(1)}-hos"

    # Cas général : "année_num_numero"
    match = re.search(r"(\d{4})_num_(\d+)", url)
    if match:
        year, number = match.groups()
        return f"{year}-{number}"

    return "unknown"


def get_all_articles():
    """Récupère les URLs de tous les articles sur Persee et les range dans un dict {clé: [urls]}"""
    all_pages_links = get_persee_issue_links()
    all_pages_links.append("https://www.persee.fr/issue/medio_0223-3843_1990_hos_1_1")

    all_articles_links = defaultdict(list)

    for link in all_pages_links:
        articles = get_persee_article_links(link)
        for article in articles:
            key = extract_key_from_url(article)
            all_articles_links[key].append(article)  # 🔥 chaque clé stocke une liste de liens

    return all_articles_links # on retransforme en dict normal si tu veux
def download_all_articles(all_articles_links):
    """Télécharge tous les articles sur Persee en positionnant exactement la souris sur le bouton téléchargement
    puis en supprimant l'onglet en se positionnant pour le supprimer.

    ⚠️ Très spécifique à la config locale (positions souris, délais, etc.).
    """
    webbrowser.open("https://www.persee.fr/collection/medio")

    for key, urls in all_articles_links.items():
        print(f"📂 Téléchargement pour la clé {key} ({len(urls)} articles)")

        for url in urls:
            webbrowser.open(url)
            time.sleep(4)  # Attendre que la page charge

            # Clique sur une position donnée (ajuste si besoin)
            pyautogui.click(x=420, y=650)  # bouton PDF
            time.sleep(1)
            pyautogui.click(x=630, y=30)   # fermer onglet

            print(f"✅ Article téléchargé : {url}")

download_all_articles(get_all_articles())