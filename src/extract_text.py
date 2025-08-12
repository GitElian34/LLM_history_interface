import PyPDF2

def extraire_texte_pdf_par_page(chemin_pdf):
    texte_par_page = {}
    with open(chemin_pdf, 'rb') as f:
        lecteur = PyPDF2.PdfReader(f)
        for i, page in enumerate(lecteur.pages):
            texte = page.extract_text() or ""
            texte_par_page[f"Page {i + 1}"] = texte  # page numérotée à partir de 1
    return texte_par_page
def text_wo_footnotes(dict_ftn, dict_txt):
    for key, page in dict_txt.items():
        if dict_ftn.get(key):  # vérifie que des footnotes existent pour cette page
            first_footnote_words = dict_ftn[key][0][:10].replace('1,', '1.')
            print("LA lES FOOTNOTES")
            print(first_footnote_words)
            print("PAAAAAAGE")
            print(page)
            marker_pos = page.find(first_footnote_words)

            if marker_pos > 0:
                print("TROUVEREEREERER \n\n \n\n")
                texte_principal = page[:marker_pos]
                footnotes = page[marker_pos:]

                # Formater les footnotes avec // au début et à la fin
                footnotes_formatees = f" <ftn>{footnotes} <ftn>"

                # Recomposer la page : texte principal + 2 sauts de ligne + footnotes formatées
                new_text = texte_principal + "\n\n" + footnotes_formatees
                print(new_text)
                dict_txt[key] = new_text

    return dict_txt
# Exemple d'utilisation
if __name__ == "__main__":
    chemin = "C:/Users/elian/Documents/stage/Recherche/pdf/1592.pdf"
    texte_par_page = extraire_texte_pdf_par_page(chemin)

    for page_num, texte in texte_par_page.items():
        print(f"\n--- Page {page_num} ---\n")
        print(texte)