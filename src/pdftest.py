import os
import pytesseract
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import re
# Configuration des chemins
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
TESSERACT_PATH = r"C:\Users\elian\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_footnotes(image_path, footer_height=0.40):
    from pprint import pprint

    #print(f"\n[INFO] Traitement de l'image : {image_path}")

    img = Image.open(image_path)
    width, height = img.size
    footer_box = (0, int(height * (1 - footer_height)), width, height)
    footer = img.crop(footer_box)

    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    text = pytesseract.image_to_string(np.array(footer), config=custom_config)

    #print("\n[DEBUG] Texte OCR extrait (repr) :")
    #print(repr(text))  # Affiche les \n, espaces, etc.

    # Regroupe les lignes en bloc
    lines = text.split('\n')
    #print("\n[DEBUG] Lignes OCR analysées :")
    #pprint(lines)

    note_pattern = re.compile(
        r'^\s*('
        r'1[,.]|'  # 1, ou 1.
        r'([1-9]|[1-9][0-9]|100)[\.\)]|'  # 1. ou 2)
        r'\(([1-9]|[1-9][0-9]|100)\)|'  # (1) ou (23)
        r'([1-9]|[1-9][0-9]|100)\s[A-Z]|'  # 1 A ou 23 B
        r'Note:'  # Mot-clé Note:
        r')'
          # Option pour rendre "Note:" insensible à la casse
    )

    notes = []
    current_note = ""

    for idx, line in enumerate(lines):
        stripped_line = line.strip()
        #print(f"\n[DEBUG] Ligne {idx + 1}: '{stripped_line}'")

        if not stripped_line:
            #print("→ Ligne vide, ignorée.")
            continue

        if note_pattern.match(stripped_line):
           # print("→ Début de nouvelle note détectée.")
            if current_note:
                #print(f"→ Note sauvegardée : {current_note.strip()}")
                notes.append(current_note.strip())
            current_note = stripped_line
        elif current_note:
            #print("→ Continuation de la note actuelle.")
            current_note += " " + stripped_line


    if current_note:
        #print(f"\n→ Dernière note sauvegardée : {current_note.strip()}")
        notes.append(current_note.strip())

   # print("\n[RESULTAT] Notes extraites :")
    #pprint(notes)

    return notes


def extract_content(image_path, footer_threshold=1):
    """Extrait le texte principal avec conservation des sauts de ligne naturels"""
    img = Image.open(image_path)
    width, height = img.size

    # Découpage en évitant la zone de footer (derniers 15% par défaut)
    main_box = (0, 0, width, int(height * footer_threshold))
    main_img = img.crop(main_box)

    # Configuration OCR optimisée pour garder la structure
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'

    # Extraction du texte brut avec sauts de ligne
    raw_text = pytesseract.image_to_string(np.array(main_img), config=custom_config)

    # Nettoyage intelligent qui conserve les sauts de ligne
    cleaned_text = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if line:  # Ne garde que les lignes non vides
            # Remplace les espaces multiples par un seul espace
            cleaned_line = ' '.join(line.split())
            cleaned_text.append(cleaned_line)

    # Recombine avec des sauts de ligne
    return '\n'.join(cleaned_text)


def process_pdf(pdf_path, output_dir="output"):
    """Extrait le contenu en séparant proprement texte principal et notes"""
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    os.makedirs(output_dir, exist_ok=True)

    results = {}  # Texte principal
    results_ftn = {}  # Notes de bas de page

    for i, img in enumerate(images):
        img_path = os.path.join(output_dir, f"page_{i + 1}.png")
        img.save(img_path, "PNG")

        # Extraction du contenu complet
        full_text = extract_content(img_path)

        # Extraction des notes
        footnotes = extract_footnotes(img_path)
        #print(f"\nPage {i + 1} - Notes détectées:", footnotes)

        # Si on a des notes, on trouve la position de la première note
        if footnotes:
            # On prend les 2-3 premiers mots de la première note comme marqueur
            first_footnote_words = ' '.join(footnotes[0].split()[:3])
            #print("\n\n\n")
            #print(first_footnote_words)

            # Trouver la position de ce marqueur dans le texte
            marker_pos = full_text.find(first_footnote_words)

            if marker_pos > 0:
                # Tout ce qui avant le marqueur est texte principal
                main_text = full_text[:marker_pos]
                # Tout ce qui après est considéré comme notes
                detected_footnotes = full_text[marker_pos:]

                #print(f"Découpage à position {marker_pos}")
                #print(f"Texte principal: {main_text[:50]}...")
                #print(f"Notes détectées: {detected_footnotes[:50]}...")



            else:
                main_text = full_text

        else:
            main_text = full_text


        # Nettoyage final
        #main_text = ' '.join(main_text.split())
        results[f"Page {i + 1}"] = main_text
        results_ftn[f"Page {i + 1}"] = footnotes

    return results, results_ftn

# Exemple d'utilisation
if __name__ == "__main__":
    pdf_path = "C:/Users/elian/Documents/stage/Recherche/pdf/1586.pdf"
    contents, foot_notes = process_pdf(pdf_path)
    print("-----------------------CONTENT----------------------------------\n")
    for content in contents.values():
        print(content)
    # for page, content in contents.items():
    #     print(f"\n{page}:")
    #     print(content)
    print("-----------------------FOOTNOTES----------------------------------\n")
    print(foot_notes)
    # for page, notes in foot_notes.items():
    #     print(f"\n{page}:")
    #     print(f"• {len(notes)} notes de bas de page:")
    #     print(notes)
    #     print("\n")
