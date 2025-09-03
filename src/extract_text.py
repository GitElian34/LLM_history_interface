import PyPDF2

def extraire_texte_pdf_par_page(chemin_pdf):
    """
    Ouvre un PDF et extrait le texte de chaque page.
    Retourne un dictionnaire { "Page n" : texte }.
    """
    texte_par_page = {}
    with open(chemin_pdf, 'rb') as f:
        lecteur = PyPDF2.PdfReader(f)
        for i, page in enumerate(lecteur.pages):
            texte = page.extract_text() or ""  # évite None si pas de texte
            texte_par_page[f"Page {i + 1}"] = texte  # clés sous forme "Page 1", "Page 2"...
    return texte_par_page


def text_wo_footnotes(dict_ftn, dict_txt):
    """
    Supprime les footnotes du texte principal et les reformate.
    - dict_txt : dictionnaire { "Page n" : texte complet }
    - dict_ftn : dictionnaire { "Page n" : footnotes détectées }
    Modifie dict_txt en plaçant les footnotes à la fin du texte avec balises <ftn>.
    """
    for key, page in dict_txt.items():
        if dict_ftn.get(key):  # si des footnotes existent pour la page
            first_footnote_words = dict_ftn[key][0][:10].replace('1,', '1.')  # extrait début footnote
            marker_pos = page.find(first_footnote_words)  # cherche où ça commence dans le texte

            if marker_pos > 0:  # si trouvé dans le texte
                texte_principal = page[:marker_pos]  # texte avant la footnote
                footnotes = page[marker_pos:]        # texte footnote

                # Formate les footnotes avec balises <ftn>
                footnotes_formatees = f" <ftn>{footnotes} <ftn>"

                # Reconstruit la page avec séparation par 2 sauts de ligne
                dict_txt[key] = texte_principal + "\n\n" + footnotes_formatees

    return dict_txt

# Exemple d'utilisation
if __name__ == "__main__":
    chemin = "C:/Users/elian/Documents/stage/Recherche/pdf/1592.pdf"
    texte_par_page = extraire_texte_pdf_par_page(chemin)

    for page_num, texte in texte_par_page.items():
        print(f"\n--- Page {page_num} ---\n")
        print(texte)