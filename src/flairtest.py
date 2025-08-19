from pathlib import Path
import sqlite3
import spacy
import re
import stanza
from flair.data import Sentence
from flair.models import SequenceTagger
from typing import Dict, List
from src.database.db_query import *
from src.database.db_setup import *
from src.database.db_insert import *
from src.extract_text import *
nlp = spacy.load("en_core_web_sm")

# 2. Flair pour la NER
tagger = SequenceTagger.load('flair/ner-english-large')
DB_PATH = Path(__file__).resolve().parent / "database" / "data.db"
methods_grade = {
    "findREN": [0, 0],
    "findREN_fulltext": [0, 0],
    "findREN_nospacy": [0, 0],
    "Stanza": [0, 0]
}



def get_all_db_data():
    """Récupère toutes les données de la table items"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Récupération de toutes les entrées
        cur.execute("SELECT * FROM items")
        rows = cur.fetchall()

        # Récupération des noms de colonnes
        column_names = [description[0] for description in cur.description]

        return {
            "columns": column_names,
            "data": rows
        }
    finally:
        conn.close()


def print_db_data():
    """Affiche le contenu de la base de données de manière formatée"""
    db_content = get_all_db_data()

    print("\n=== CONTENU DE LA BASE DE DONNÉES ===")
    print(f"Colonnes: {', '.join(db_content['columns'])}")
    print("-" * 60)

    for row in db_content['data']:
        print(f" Mot: '{row[0]}' | Type: {row[1]} | Méthode: {row[2]}")
stanza_nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')


def normalize_string(s):
    """Normalise une chaîne pour la comparaison"""
    # Supprime espaces, tirets, normalise la casse
    return re.sub(r'[\s-]', '', s).lower()


def is_entity_in_data(db_entity, true_data_list):
    """Vérifie si l'entité de la DB est contenue dans un élément des données de référence
    ou si l'un des mots de la référence est contenu dans l'entité de la DB"""
    normalized_db = normalize_string(db_entity)

    for true_entity in true_data_list:
        normalized_true = normalize_string(true_entity)

        # Vérification 1: l'entité DB est contenue dans la référence
        if normalized_db in normalized_true:
            return True

        # Vérification 2: l'un des mots de la référence est dans l'entité DB
        for word in normalized_true.split():
            if word in normalized_db:
                return True

    return False

def find_entities_stanza(text: str, entities_by_type: Dict[str, List[str]]):
    """Utilisation de Stanza pour la NER"""
    doc = stanza_nlp(text)
    for sentence in doc.sentences:
        for entity in sentence.ents:
            if entity.type == 'PERSON':
                entities_by_type['PERSON'].append(entity.text)
                methods_grade["Stanza"][1] += 1
                normalized_word = re.sub(r'[\s-]', '', entity.text).lower()
                insert_item(normalized_word, "PERSON", "Stanza")
            elif entity.type in ['LOC', 'GPE']:
                entities_by_type['LOC'].append(entity.text)
                methods_grade["Stanza"][1] += 1
                normalized_word = re.sub(r'[\s-]', '', entity.text).lower()
                insert_item(normalized_word, "LOC", "Stanza")
            elif entity.type == 'ORG':
                entities_by_type['ORG'].append(entity.text)
                methods_grade["Stanza"][1] += 1
                normalized_word = re.sub(r'[\s-]', '', entity.text).lower()
                insert_item(normalized_word, "ORG", "Stanza")
def findREN(text: str,threshold : float, entities_by_type: Dict[str, List[str]]):
    """Méthode originale avec spaCy + Flair"""
    doc = nlp(text)
    for sent in doc.sents:
        flair_sentence = Sentence(sent.text)
        tagger.predict(flair_sentence)

        for entity in flair_sentence.get_spans('ner'):
            entity_text = entity.text
            entity_label = entity.tag
            confidence = entity.score   # 🔥 score de certitude
            normalized_word = re.sub(r'[\s-]', '', entity_text).lower()

            print(f"Trouvé: {entity_text} | Label: {entity_label} | Confiance: {confidence:.2f}")

            if entity_label == 'PER' and confidence > threshold:
                entities_by_type['PERSON'].append(entity_text)
                methods_grade["findREN"][1] += 1
               # insert_item(normalized_word, "PERSON", "findREN", pertinence=f"{confidence:.2f}")
            elif entity_label in ['LOC', 'GPE'] and confidence > threshold:
                entities_by_type['LOC'].append(entity_text)
                methods_grade["findREN"][1] += 1
                #insert_item(normalized_word, "LOC", "findREN", pertinence=f"{confidence:.2f}")
            elif entity_label == 'ORG' and confidence > threshold:
                entities_by_type['ORG'].append(entity_text)
                methods_grade["findREN"][1] += 1
                #insert_item(normalized_word, "ORG", "findREN", pertinence=f"{confidence:.2f}")


def findREN_nospacy(text: str, entities_by_type: Dict[str, List[str]]):
    """Extraction avec segmentation simple sans spaCy"""
    sentences = re.split(r'[.!?]\s+', text)
    for sent in sentences:
        if sent.strip():
            flair_sentence = Sentence(sent)
            tagger.predict(flair_sentence)

            for entity in flair_sentence.get_spans('ner'):
                entity_text = entity.text
                entity_label = entity.tag
                normalized_word = re.sub(r'[\s-]', '', entity_text).lower()

                if entity_label == 'PER':
                    entities_by_type['PERSON'].append(entity_text)
                    methods_grade["findREN_nospacy"][1] += 1
                    insert_item(normalized_word, "PERSON", "findREN_nospacy")
                elif entity_label in ['LOC', 'GPE']:
                    entities_by_type['LOC'].append(entity_text)
                    methods_grade["findREN_nospacy"][1] += 1
                    insert_item(normalized_word, "LOC", "findREN_nospacy")
                elif entity_label == 'ORG':
                    entities_by_type['ORG'].append(entity_text)
                    methods_grade["findREN_nospacy"][1] += 1
                    insert_item(normalized_word, "ORG", "findREN_nospacy")


def findREN_fulltext(text: str, entities_by_type: Dict[str, List[str]]):
    """Extraction sur tout le texte en une seule passe"""
    flair_sentence = Sentence(text)
    tagger.predict(flair_sentence)

    for entity in flair_sentence.get_spans('ner'):
        entity_text = entity.text
        entity_label = entity.tag
        normalized_word = re.sub(r'[\s-]', '', entity_text).lower()

        if entity_label == 'PER':
            entities_by_type['PERSON'].append(entity_text)
            methods_grade["findREN_fulltext"][1] += 1
            insert_item(normalized_word, "PERSON", "findREN_fulltext")
        elif entity_label in ['LOC', 'GPE']:
            entities_by_type['LOC'].append(entity_text)
            methods_grade["findREN_fulltext"][1] += 1
            insert_item(normalized_word, "LOC", "findREN_fulltext")
        elif entity_label == 'ORG':
            entities_by_type['ORG'].append(entity_text)
            methods_grade["findREN_fulltext"][1] += 1
            insert_item(normalized_word, "ORG", "findREN_fulltext")



def filldatabase(text):
    # # Test avec méthode originale (spaCy)
    reset_database()
    for page_num, page in text.items():
        entities_by_type = {'PERSON': [], 'LOC': [], 'ORG': []}
        print("\n--- Avec spaCy ---")
        findREN(page,0.90 ,entities_by_type)
        print({k: set(v) for k, v in entities_by_type.items()})

        # # # Test sans spaCy
        entities_by_type = {'PERSON': [], 'LOC': [], 'ORG': []}
        print("\n--- Sans spaCy ---")
        findREN_nospacy(page, entities_by_type)
        print({k: set(v) for k, v in entities_by_type.items()})
        #
        # # Test texte entier
        entities_by_type = {'PERSON': [], 'LOC': [], 'ORG': []}
        print("\n--- Texte entier ---")
        findREN_fulltext(page, entities_by_type)
        print({k: set(v) for k, v in entities_by_type.items()})
        entities_by_type = {'PERSON': [], 'LOC': [], 'ORG': []}
        print("\n--- STANZA---")
        find_entities_stanza(page, entities_by_type)
        print({k: set(v) for k, v in entities_by_type.items()})

def compare_method(true_data):
    """
    Compare les entités détectées avec les données de référence (true_data).
    Chaque élément de true_data ne peut être reconnu qu'une seule fois par méthode (row[2]).
    """
    tab = []
    db_content = get_all_db_data()

    # Dictionnaire pour mémoriser les entités déjà validées par méthode
    # Exemple : {"findREN": set(["barackobama", "etatsunis"]), "autreMethod": set([...])}
    matched_by_method = {}

    for row in db_content['data']:
        word, type_, method = row[0], row[1], row[2]

        # Initialiser l'ensemble pour cette méthode si besoin
        if method not in matched_by_method:
            matched_by_method[method] = set()

        # Vérifier si cette entité correspond à une des références
        for true_entity in true_data:
            normalized_true = normalize_string(true_entity)
            normalized_word = normalize_string(word)

            if len(word) > 2 and (
                normalized_word in normalized_true or
                any(w in normalized_word for w in normalized_true.split())
            ):
                # Vérifier si cette true_entity n'a pas déjà été comptée pour cette méthode
                if normalized_true not in matched_by_method[method]:
                    methods_grade[method][0] += 1
                    matched_by_method[method].add(normalized_true)  # marquer comme compté


                break  # sortir de la boucle sur true_data pour éviter plusieurs matches du même mot
        else:
            methods_grade[method][0] -= 0.0  # ne change rien, garde la logique existante

    return methods_grade


if __name__ == "__main__":
    input_path = "C:/Users/elian/Documents/stage/Recherche/pdf/1586.pdf"
    text = extraire_texte_pdf_par_page(input_path)
    print(text)
    filldatabase(text)
    true_data = ["Europe","Allemagne","Munich","Pays-Bas","Autriche","Emil Friedberg","Heinrich von Sybel"
                 ,"Theodor von Sickel","Markus Brantl","Georg Vogeler","BSB","DFG","Ludwig-Maximilian","Lizartech","Lehrstuhl für Geschichtliche Hilfswissenschaften"
                 ,"AT&T","Kaiserurkunden","Charles Le Chauve"]
    print(compare_method(true_data))

