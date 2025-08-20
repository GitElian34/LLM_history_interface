from sqlite3 import IntegrityError

import requests
import re
import pdftest
from docx import Document
from docx.shared import Pt, RGBColor
import PyPDF2
from typing import Optional
import tkinter as tk
from tkinter import messagebox
#from pdftotext import PdftoText
from collections import *
from appli_Demo import SearchApp
from typing import Union, List, Tuple

from src.database.db_insert import insert_item, insert_processed_text
from src.database.db_query import *
#from src.SQL.crud import *
#from src.SQL.config import SessionLocal, get_db
#from src.SQL.main import init_db
from src.pdftest import process_pdf
from flairtest import findREN
from src.inteface.interface_graphique import TextAppController
from src.extract_text import *

class PDFTextProcessor:
    def __init__(self):
        """Initialise le processeur de texte PDF"""
        self.interface_controller = TextAppController()
        self.llms = ["llama3","gemma","llama2","mistral"]
        self.currentdates = {}
        self.periode_histo = []
        self.periode_histo_ftn = []
        self.data_clear=[]

        self.entities_by_type = {
        'PERSON': [],
        'LOC': [],
        'ORG': []
    }
        self.text_clean = None
        self.app_content = None
        self.pdftotext = None
        self.content = None
        self.foot_notes = None
        self.ftn_year = {}
        self.LLM_entities = None
        self.db = None

    def ask_ollama(self, prompt: str, model: str ) -> Optional[str]:
        """
        Envoie une requête à l'API Ollama.

        Args:
            prompt: Prompt à envoyer
            model: Modèle à utiliser (par défaut: "mistral")

        Returns:
            str: Réponse de l'API si succès, None sinon
        """
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            return response.json().get("response")
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête à Ollama: {str(e)}")
            return None
        except Exception as e:
            print(f"Erreur inattendue: {str(e)}")
            return None

    def split_text(self, text: str, max_length: int = 2000, overlap: int = 100) -> List[str]:
        """
        Découpe un long texte en plusieurs parties avec un chevauchement pour garder le contexte.

        Args:
            text: Texte à découper
            max_length: Longueur maximale de chaque partie (défaut: 2000 caractères)
            overlap: Nombre de caractères de chevauchement entre parties (défaut: 100)

        Returns:
            Liste des parties du texte
        """
        if len(text) <= max_length:
            return [text]

        parts = []
        start = 0

        while start < len(text):
            end = start + max_length
            # Trouve le dernier point/saut de ligne dans la limite
            split_at = text.rfind('\n', start, end)
            if split_at == -1 or split_at < start + (max_length // 2):
                split_at = text.rfind('. ', start, end)
                if split_at != -1:
                    split_at += 1  # Inclure le point

            if split_at == -1 or split_at < start + (max_length // 2):
                split_at = end

            part = text[start:split_at].strip()
            if part:
                parts.append(part)

            # Début suivant avec chevauchement
            start = max(split_at - overlap, start + 1)

        return parts


    def ask_question(self,question: str,content: str, llm :str) -> Optional[str]:

        full_prompt = f"{content}\n\n{question}"
        return self.ask_ollama(full_prompt, llm)

    import re
    from typing import List, Union, Tuple

    def extraire_annees_historiques(self, texte: str,epoques) -> List[Union[int, Tuple[int, int]]]:
        """
        Extrait les années historiques (3 ou 4 chiffres, plages d'années, et siècles '12th', '13th century', etc.)
        Retourne une liste sans doublons avec des entiers pour les années simples
        et des tuples pour les plages (début, fin).
        """
        result = []
        seen = set()

        roman_to_int = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
            'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
            'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
            'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20
        }
        matches = re.findall(r'\b(\d{3,4})\b', texte)
        h_matches=re.findall( r'\[([A-ZÀ-ÿ][^\]]+)\]',texte)
        for nb in matches:
            try:
                num = int(nb)
                if num not in seen:  # Évite les doublons
                    result.append(num)
                    seen.add(num)
            except ValueError:  # Sécurité si conversion échoue
                print(f"Valeur numérique invalide : {nb}")

        # Traitement des périodes historiques
        for h_ep in h_matches:
            if h_ep not in epoques:  # Évite les doublons
                print(f"Période historique trouvée : {h_ep}")  # Debug optionnel
                epoques.append(h_ep)

        # 1. Années simples ou plages : 950, 1200-1250
        # matches = re.findall(r'\b(\d{3,4})\b(?:-(\d{3,4})\b)?', texte)
        # for debut_str, fin_str in matches:
        #     debut = int(debut_str)
        #     if fin_str:
        #         fin = int(fin_str)
        #         if (debut, fin) not in seen:
        #             result.append((debut, fin))
        #             seen.add((debut, fin))
        #     elif debut not in seen:
        #         result.append(debut)
        #         seen.add(debut)

        # 1. Extraction des siècles numériques (12th, 13th century/siècle)
        numeric_pattern = r'\b(\d{1,2})(?:st|nd|rd|th|e)\s*(?:century|siècle)?\b'
        for century_str in re.findall(numeric_pattern, texte, re.IGNORECASE):
            century = int(century_str)
            debut = (century - 1) * 100
            fin = century * 100
            if (debut, fin) not in seen:
                result.append((debut, fin))
                seen.add((debut, fin))

        # 2. Extraction des chiffres romains (XV, XII siècle/century)
        roman_pattern = r'\b(X{0,3}I{0,3}X?I{0,3})\s*(?:century|siècle|e)\b'
        for roman in re.findall(roman_pattern, texte, re.IGNORECASE):
            if roman.upper() in roman_to_int:
                century = roman_to_int[roman.upper()]
                debut = (century - 1) * 100
                fin = century * 100
                if (debut, fin) not in seen:
                    result.append((debut, fin))
                    seen.add((debut, fin))

        #print(result)

        return sorted(result, key=lambda x: x[0] if isinstance(x, tuple) else x)

    def compter_occurrences_manuel(self, nombres, list):
        for nombre in nombres:
            if nombre in list:
                list[nombre] += 1
            else:
                list[nombre] = 1
        return list

    def clear_data(self, seuil: int, dico) -> List[Union[int, Tuple[int, int]]]:
        return [key for key, count in dico.items() if count >= seuil]

    def stringtoword(self,text: str) :
        doc = Document()
        p = doc.add_paragraph()
        p.add_run(text)

        # Ajouter du texte en grande taille

        doc.save("C:/Users/elian/Documents/stage/Recherche/output/output.docx")
        return doc

    def dict_to_text(self,dictionary):
        text = ""
        for page, content in dictionary.items():
            text += f"{page}:\n{content}\n\n"  # \n\n pour saut de ligne double entre pages
        return text.strip()  # .strip() pour supprimer le dernier \n inutile

    import re
    from typing import List

    def extract_and_store(self, dict_, nombres_cibles, entities_by_type, epoques_cible: List[str], article_id, pattern=None):
        """
        Parcourt les textes dans le dictionnaire et insère en BDD les entités trouvées
        (PERSON, LOC, ORG, nombres, époques), sans modifier le texte.

        Args:
            dict_: Dictionnaire contenant les valeurs à analyser
            nombres_cibles: Liste de nombres à détecter
            entities_by_type: Dictionnaire contenant les entités classées par type (PERSON, LOC, ORG)
            epoques_cible: Liste d'époques à détecter
            article_id: ID de l'article auquel rattacher les entités
            pattern: Optionnel - motif regex prédéfini (non utilisé ici)

        Returns:
            None (insertion uniquement en BDD)
        """
        # Convertir les nombres en strings une fois pour toutes
        nombres_str = list(map(str, nombres_cibles))

        # Traiter chaque valeur du dictionnaire
        for key, value in dict_.items():
            current_text = str(value)

            # === PERSON ===
            for entity in entities_by_type.get("PERSON", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                if re.search(pattern, current_text, flags=re.IGNORECASE):
                    insert_item(article_id, cleaned, "PERSON", "findREN")

            # === LOC ===
            for entity in entities_by_type.get("LOC", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                if re.search(pattern, current_text, flags=re.IGNORECASE):
                    insert_item(article_id, cleaned, "LOC", "findREN")

            # === ORG ===
            for entity in entities_by_type.get("ORG", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                if re.search(pattern, current_text, flags=re.IGNORECASE):
                    insert_item(article_id, cleaned, "ORG", "findREN")

            # === Nombres ===
            for num in nombres_str:
                pattern = r'(?<!\w)(' + re.escape(num) + r')(?!\w)'
                if re.search(pattern, current_text):
                    insert_item(article_id, num, "Number", "LLM")

            # === Époques ===
            for epoque in epoques_cible:
                cleaned = epoque.replace(" ", "_").replace("-", "_")

                pattern = r'(?<!\w)(' + re.escape(epoque) + r')(?!\w)'
                if re.search(pattern, current_text, flags=re.IGNORECASE):
                    insert_item(article_id, cleaned, "Period", "LLM")

    def number_to_bold_noDB(self, dict, nombres_cibles, entities_by_type, epoques_cible: List[str], pattern=None):
        """
        Identique à number_to_bold mais sans insertion en base de données.
        Met en évidence nombres, entités et époques dans les valeurs du dictionnaire.

        Args:
            dict: Dictionnaire contenant les valeurs à modifier
            nombres_cibles: Liste de nombres à mettre en évidence
            entities_by_type: Dictionnaire contenant les entités classées par type (PERSON, LOC, ORG)
            epoques_cible: Liste d'époques à mettre en évidence
            pattern: Optionnel - motif regex prédéfini (non utilisé dans cette version)

        Returns:
            Le dictionnaire modifié
        """
        # Convertir les nombres en strings une fois pour toutes
        nombres_str = list(map(str, nombres_cibles))

        # Traiter chaque valeur du dictionnaire
        for key, value in dict.items():
            current_text = str(value)  # Conversion en string pour sécurité

            # === PERSON ===
            for entity in entities_by_type.get("PERSON", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_person(match):
                    found = match.group(1)
                    return f'++{cleaned}++'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_person, current_text, flags=re.IGNORECASE)

            # === LOC ===
            for entity in entities_by_type.get("LOC", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_loc(match):
                    found = match.group(1)
                    return f'@@{cleaned}@@'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_loc, current_text, flags=re.IGNORECASE)

            # === ORG ===
            for entity in entities_by_type.get("ORG", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_org(match):
                    found = match.group(1)
                    return f'┤┤{cleaned}┤┤'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_org, current_text, flags=re.IGNORECASE)

            # === Nombres ===
            for num in nombres_str:
                pattern = r'(?<!\w)(' + re.escape(num) + r')(?!\w)'

                def replacer_num(match):
                    found = match.group(1)
                    return f'**{found}**'

                current_text = re.sub(pattern, replacer_num, current_text)

            # === Époques ===
            for epoque in epoques_cible:
                cleaned = epoque.replace(" ", "_").replace("-", "_")

                def replacer_epoque(match):
                    found = match.group(1)
                    return f'¦¦{cleaned}¦¦'

                pattern = r'(?<!\w)(' + re.escape(epoque) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_epoque, current_text, flags=re.IGNORECASE)

            # Mettre à jour la valeur dans le dict
            dict[key] = current_text

        return dict

    def number_to_bold_withDB(self, dict, article_id: int, nombres_cibles, entities_by_type, epoques_cible: List[str],
                              pattern=None):
        """
        Met en évidence nombres, entités et époques dans les valeurs du dictionnaire
        ET insère chaque élément dans la base de données.

        Args:
            dict: Dictionnaire contenant les valeurs à modifier
            article_id: ID de l'article pour insertion en BDD
            nombres_cibles: Liste de nombres à mettre en évidence
            entities_by_type: Dictionnaire contenant les entités classées par type (PERSON, LOC, ORG)
            epoques_cible: Liste d'époques à mettre en évidence
            pattern: Optionnel - motif regex prédéfini (non utilisé ici)

        Returns:
            Le dictionnaire modifié
        """
        # Convertir les nombres en strings une fois pour toutes
        nombres_str = list(map(str, nombres_cibles))

        for key, value in dict.items():
            current_text = str(value)  # Sécurité

            # === PERSON ===
            for entity in entities_by_type.get("PERSON", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_person(match):
                    insert_item(article_id, entity, "PERSON", "highlight")  # insertion BDD
                    return f'++{cleaned}++'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_person, current_text, flags=re.IGNORECASE)

            # === LOC ===
            for entity in entities_by_type.get("LOC", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_loc(match):
                    insert_item(article_id, entity, "LOC", "highlight")
                    return f'@@{cleaned}@@'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_loc, current_text, flags=re.IGNORECASE)

            # === ORG ===
            for entity in entities_by_type.get("ORG", []):
                cleaned = entity.replace(" ", "_").replace("-", "_").replace(".", "\u00B7").replace("'", "\u02BC")

                def replacer_org(match):
                    insert_item(article_id, entity, "ORG", "highlight")
                    return f'┤┤{cleaned}┤┤'

                pattern = r'(?<!\w)(' + re.escape(entity) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_org, current_text, flags=re.IGNORECASE)

            # === Nombres ===
            for num in nombres_str:
                pattern = r'(?<!\w)(' + re.escape(num) + r')(?!\w)'

                def replacer_num(match):
                    found = match.group(1)
                    insert_item(article_id, found, "Number", "highlight")
                    return f'**{found}**'

                current_text = re.sub(pattern, replacer_num, current_text)

            # === Époques ===
            for epoque in epoques_cible:
                cleaned = epoque.replace(" ", "_").replace("-", "_")

                def replacer_epoque(match):
                    found = match.group(1)
                    insert_item(article_id, found, "Period", "highlight")
                    return f'¦¦{cleaned}¦¦'

                pattern = r'(?<!\w)(' + re.escape(epoque) + r')(?!\w)'
                current_text = re.sub(pattern, replacer_epoque, current_text, flags=re.IGNORECASE)

            # Mise à jour de la valeur dans le dict
            dict[key] = current_text

        return dict


    def replacenum(self, text: str, nombres_cibles,color: RGBColor,epoques_cible: List[str],output ):
        # 1. Conversion du texte en document Word
        doc = self.stringtoword(text)

        # 2. Création des motifs séparés
        # Pattern pour les nombres (sans insensibilité à la casse)
        pattern_nombres = re.compile(
            r'(?<!\w)(' + '|'.join(map(re.escape, map(str, nombres_cibles))) + r')(?!\w)'
        )
        print(pattern_nombres)

        # Pattern pour les époques (avec insensibilité à la casse)

        pattern_epoques = re.compile(
            r'(?<!\w)(' + '|'.join(map(re.escape, epoques_cible)) + r')(?!\w)',
            flags=re.IGNORECASE
        )

        print(pattern_epoques)
        # 3. Fusion des motifs en un seul pattern
        # 3. Fusion des motifs en un seul patterngit
        combined_pattern = re.compile(
            f"({pattern_nombres.pattern}|{pattern_epoques.pattern})",
            flags=re.IGNORECASE | re.DOTALL | re.MULTILINE
        )
        print(f"Pattern combiné : {combined_pattern.pattern}")

        # 3. Traitement des paragraphes
        for paragraph in doc.paragraphs:
            # Création d'une liste temporaire pour les runs
            new_runs = []
            current_text = paragraph.text

            # Trouver toutes les occurrences
            matches = list(combined_pattern.finditer(current_text))
            if not matches:
                continue

            # Reconstruire le paragraphe
            last_end = 0
            for match in matches:
                # Texte avant le match
                if last_end < match.start():
                    new_runs.append((current_text[last_end:match.start()], False))

                # Texte du match (à formater)
                new_runs.append((match.group(), True))
                last_end = match.end()

            # Texte après le dernier match
            if last_end < len(current_text):
                new_runs.append((current_text[last_end:], False))

            # Réappliquer le formatage
            paragraph.clear()

            for text, should_format in new_runs:
                run = paragraph.add_run(text)
                if should_format:

                    run.bold = True
                    run.font.size = Pt(14)
                    run.font.color.rgb = color
    # def initdatabase(self):
    #     """Initialise la base de données sans supprimer les entrées existantes"""
    #     init_db()  # S'assure que les tables existent
    #     self.db = next(get_db())
    def getdataLLM(self,iter:int,contenu , nbllm:int,epoques, question: str, result ):
        contexte = ("Mon objectif est de prendre un pdf et de mettre en avant toutes"
                    "les dates et périodes historiques en les mettants en gras et plus gros"
                    "d'où l'importace que tu me mettes uniquement ce que tu vois et pas ce que tu déduis \n")
        prompt = question
        for i in range(0, nbllm):

            for j in range(0, iter):

                for page in contenu.values():
                   # print("LA PAGE RESSEMBLE A \n")
                   # print(page)
                    response = self.ask_question(prompt, page, self.llms[i])
                    if response:
                        print("Réponse reçue:")
                        #print(page)
                        #print(response)
                        annees_trouve = self.extraire_annees_historiques(response,epoques)
                        print(annees_trouve)
                        self.compter_occurrences_manuel(annees_trouve, result)
                        if type(page) != list:

                            findREN(page, 0.80,self.entities_by_type)


                    else:
                        print("Le traitement a échoué.")
        print("Fin du traitement")


    def FillDB(self, iter:int, nbllm:int,seuil :int, question: str,input_path: str,article_id: int ):
        pdf_path = input_path
        print("DEBUT DU TEST")
        #content = self.pdftotext.clean_content
        self.content,self.foot_notes= process_pdf(pdf_path)

        #print(self.content)
        self.getdataLLM(iter,self.content,nbllm,self.periode_histo,question,self.currentdates)
        self.data_clear = self.clear_data(seuil,self.currentdates)

        self.getdataLLM(iter,self.foot_notes,1,self.periode_histo_ftn,question,self.ftn_year)


        self.texte_clean = text_wo_footnotes(self.foot_notes,extraire_texte_pdf_par_page(input_path))
        self.number_to_bold_withDB(self.texte_clean, article_id,self.data_clear, self.entities_by_type, self.periode_histo)
        insert_processed_text(article_id,self.texte_clean)


    def Test_with_BDD(self,pdf_path,article_id):

        self.content, self.foot_notes = process_pdf(pdf_path)
        self.texte_clean = text_wo_footnotes(self.foot_notes, extraire_texte_pdf_par_page(pdf_path))


        self.data_clear = get_numbers(article_id)
        self.entities_by_type = get_entities(article_id)
        self.periode_histo = get_epoques(article_id)
        self.app_content = self.number_to_bold_noDB(self.texte_clean, self.data_clear, self.entities_by_type, self.periode_histo)


if __name__ == "__main__":
    print("début du programme")
    processor = PDFTextProcessor()
    question1 = ("Quelles sont les périodes historiques couvertes par ce document ?"
                 " Si une période précise est mentionnée (comme un siècle,"
                 " par exemple 'XIIIe siècle (1200-1300)'), indiquez-la clairement "
                 "en précisant les années concernées. Mentionnez également toute année"
                 " spécifique en rapport avec cette période.")

    question2 = """Analysez le document et :
    - Identifiez les périodes historiques principales évoquées
    - Concentre toi UNIQUEMENT sur les années et période historiques anciennes
    -ets les période historique entre crochet exemple :[Moyen Age]
    Fournissez une réponse synthétique."""

    question3 = """Extrait du texte tout ce qui pourrait s'apparenter à une année entre l'an 0 et l'an 2020 je ne veux aucune explication
    simplement que tu écrives toutes les années anciennes ou nouvelles que tu as trouvé, en évitant tous les nombres
    que tu ne considères pas comme des années. Mets les période historique entre crochet exemple :[Moyen Age]"""

    question4 = """Relève simplement toutes les années et période historique de cet article scientifique, cela peut être
    des années comme des Noms propres ex: Moyen Age,grande depression...  N'invente RIEN, uniquement des dates et périodes que je
    pourraient voir écrite dans l'article. Mets les période historique entre crochet exemple :[Moyen Age]"""

    question5 = (
        "Analysez ce texte académique en histoire médiévale et listez toutes les années non modernes:\n"
        "1. Liées aux événements historiques décrits (dates d'actes, règnes, batailles)\n"
        "2. Mentionnées dans le contexte des documents médiévaux étudiés\n"
        "3. Relatives aux périodes couvertes par les projets d'édition\n\n"

        "Exclure explicitement :\n"
        "- Les dates de publication/modernes\n"
        "- Toutes les dates qui font parties des citations bibliographiques\n"
        "- Les références bibliographiques contemporaines\n\n"

        "Format de sortie exigé :\n"
        "- Liste unique d'années triées par ordre croissant\n"
        "- Aucun commentaire, contexte ou explication\n"
        "- Inclure les années isolées ET les plages (ex: 1214-1322)\n\n")
    question6 = ("""Relève simplement tout ce qui pourrait s'apparenter à une année, nouvelle ou ancienne dans ce texte
    """)
    article_id = 1586
    PATH = "C:/Users/elian/Documents/stage/Recherche/pdf/"
    article_PATH = f"{PATH}{article_id}.pdf"
    #article_path=PATH+str(num_article)+".pdf"
    #processor.Test(1, 1, 1, question4,PATH)
    processor.FillDB(1, 1, 1, question4,article_PATH,article_id)
    #processor.Test_with_BDD(article_PATH,article_id)
    root = tk.Tk()

    processor.interface_controller.launch_app(processor.app_content,article_id,data_processor=processor)
    root.mainloop()