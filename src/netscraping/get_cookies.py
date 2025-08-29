import pyautogui
import time
import webbrowser
from netscraping2 import *
# Ouvre l'article dans ton navigateur par défaut
def get_all_articles() :
    all_pages_links = get_persee_issue_links()
    all_pages_links.append("https://www.persee.fr/issue/medio_0223-3843_1990_hos_1_1")
    all_articles_links=[]
    for link in all_pages_links :
        articles = get_persee_article_links(link)
        for article in articles :
            all_articles_links.append(article)

    return all_articles_links

def donwnload_all_articles(all_articles_links):
    webbrowser.open("https://www.persee.fr/collection/medio")
    for article in all_articles_links :
        url = article
        webbrowser.open(url)

        time.sleep(4)  # Attendre que la page charge

        # Clique sur une position donnée (x=800, y=450 par exemple)

        pyautogui.click(x=420, y=650)
        time.sleep(1)
        pyautogui.click(x=630, y=30)

        print("✅ Clic effectué sur le bouton PDF")

donwnload_all_articles(get_all_articles())