import requests
from bs4 import BeautifulSoup
import re


def get_persee_issue_links(collection_url="https://www.persee.fr/collection/medio"):
    """
    Récupère tous les liens vers les numéros d'une revue sur Persée.

    Args:
        collection_url (str): URL de la page de la collection.

    Returns:
        list: Liste des URLs des numéros.
    """
    response = requests.get(collection_url)
    if response.status_code != 200:
        print(f"Erreur : impossible de récupérer la page ({response.status_code})")
        return []

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Tous les liens <a> avec un href
    links = soup.find_all("a", href=True)

    # Pattern pour capturer tous les numéros de la revue
    pattern = re.compile(r"https://www\.persee\.fr/issue/medio_\d{4}-\d{4}_\d{4}_num_\d+_\d+")

    # Filtrer les liens correspondant au pattern
    issue_links = [link['href'] for link in links if pattern.match(link['href'])]

    # Supprimer les doublons et trier
    issue_links = sorted(list(set(issue_links)))

    # Affichage
    print(f"Nombre de numéros récupérés : {len(issue_links)}")
    for l in issue_links:
        print(l)

    return issue_links


def get_persee_article_links(issue_url):
    """
    Récupère tous les liens d'articles d'une page de numéro Persée.

    Args:
        issue_url (str): URL de la page du numéro.

    Returns:
        list: Liste des URLs des articles.
    """
    response = requests.get(issue_url)
    if response.status_code != 200:
        print(f"Erreur : impossible de récupérer la page ({response.status_code})")
        return []

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Tous les liens <a> avec un href
    links = soup.find_all("a", href=True)

    # Pattern simplifié pour tous les articles "medio"
    pattern = re.compile(r"https://www\.persee\.fr/doc/medio_\S+")

    # Filtrer les liens correspondant au pattern
    article_links = [link['href'] for link in links if pattern.match(link['href'])]

    # Supprimer les doublons et trier
    article_links = sorted(list(set(article_links)))

    # Affichage
    print(f"Nombre de liens Persée filtrés : {len(article_links)}")
    for l in article_links:
        print(l)

    return article_links

# Exemple d'utilisation
all_issues = get_persee_issue_links()
all_issues.append("https://www.persee.fr/issue/medio_0223-3843_1990_hos_1_1")
get_persee_article_links(all_issues[1])

