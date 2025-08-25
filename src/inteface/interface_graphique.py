import re

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QPushButton, QHBoxLayout, QToolTip, QDialog, QLabel, QCheckBox, QRadioButton,
                             QButtonGroup, QComboBox, QLineEdit, QDialogButtonBox)
from PyQt6.QtGui import QFont, QTextCharFormat
from PyQt6.QtCore import Qt

from src.database.db_insert import update_pertinence, insert_item
from src.database.db_query import get_all_articles, get_article_pages


class MultiPageTextApp(QMainWindow):
    def __init__(self, article_id, pages = None,data_processor = None, controller=None):
        super().__init__()
        self.data_processor = data_processor
        self.controller = controller  # référence au controller
        self.setWindowTitle("Interface Graphique")
        self.resize(800, 600)
        self.current_page = 0  # Page actuelle
        # Contenu des pages (peut être chargé depuis un fichier)
        self.pages = pages if pages is not None else []
        # Widget central et layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        self.article_combo = QComboBox()
        self.article_combo.addItems([str(a) for a in get_all_articles()])  # liste des articles
        self.article_combo.setCurrentText(str(article_id))
        self.article_combo.currentIndexChanged.connect(self.change_selected_article)
        top_layout.addWidget(self.article_combo)
        main_layout.addLayout(top_layout)

        self.add_button = QPushButton("Ajouter")
        self.add_button.clicked.connect(self.open_add_word_dialog)

        top_layout.addWidget(self.add_button)


        # Zone de texte
        self.text_edit = HoverTextEdit(self.pages,article_id,self.current_page)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Georgia", 12))
        self.text_edit.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)


        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.text_edit)

        # Boutons de navigation
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Précédent")
        self.prev_button.clicked.connect(self.go_to_previous_page)
        self.next_button = QPushButton("Suivant →")
        self.next_button.clicked.connect(self.go_to_next_page)

        self.refresh_button = QPushButton("Actualiser")
        self.refresh_button.clicked.connect(self.refresh_current_page)
        self.refresh_button.setToolTip("Recharger la page courante")

        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.next_button)
        main_layout.addLayout(button_layout)

        # Afficher la première page
        self.display_page()

    def change_selected_article(self):
        selected_article = self.article_combo.currentText()
        print(f"Article sélectionné : {selected_article}")
        new_article =get_article_pages(selected_article)
        self.controller.pagetoIG(new_article)
        #self.controller.pagetoIG(get_article_pages(selected_article))
        self.current_page = 0
        self.display_page()
        # PATH = "C:/Users/elian/Documents/stage/Recherche/pdf/"
        # article_PATH = f"{PATH}{selected_article}.pdf"
        # if self.controller is not None:
        #     # Récupère le contenu du nouvel article depuis ta DB ou autre
        #     content = self.data_processor.Test_with_BDD(article_PATH,selected_article)  # à adapter selon ta fonction
        #     # Met à jour les pages via le controller
        #    # self.controller.pagetoIG(content)
        #     # Recharge les pages dans l'interface
        #    # self.current_page = 0
        #    # self.display_page()

    def refresh_current_page(self):
        """Recharge la page actuelle"""
        self.display_page()

    def display_page(self):
        """Affiche la page actuelle avec le numéro en bas à droite."""
        # Crée un mot de test avec une infobulle (attribut title)


        # Crée le contenu principal + footer
        content = f"""
        <div style="position: relative; min-height: 95%; padding: 20px;">

            {self.pages[self.current_page]}

            <!-- Numéro de page en bas à droite -->
            <div style="
                position: absolute;
                bottom: 10px;
                right: 20px;
                color: #666;
                font-size: 12px;
                background-color: #f0f0f0;
                padding: 2px 8px;
                border-radius: 10px;
            ">
                Page {self.current_page + 1}/{len(self.pages)}
            </div>
        </div>
        """

        self.text_edit.setHtml(content)
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < len(self.pages) - 1)
    def go_to_previous_page(self):
        """Aller à la page précédente."""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def go_to_next_page(self):
        """Aller à la page suivante."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.display_page()


    def open_add_word_dialog(self):
        print("Ajouter")
        dialog = AddWordDialog()
        print("1")
        dialog.exec()


    # def update_page(self, page_number: int, raw_text: str):
    #     if page_number >= len(self.pages):
    #         self.pages.append("")
    #                     # Convertit **mot** en <b>mot</b>
    #     formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', raw_text)
    #         # Gère les sauts de ligne
    #     formatted_text = formatted_text.replace(chr(10), "<br>")
    #
    #         # Encadre le tout dans une div stylisée
    #     html_content = f"""
    #     <div style="font-family: Georgia; font-size: 14px; text-align: justify; padding: 10px;">
    #         {formatted_text}
    #     </div>
    #     """
    #
    #     self.pages[page_number] = html_content
    #
    #     if self.current_page == page_number:
    #         self.display_page()


class TextAppController:
    def __init__(self):
        self.data_processor = None
        self.pages = [
            # Votre contenu initial des pages ici
            """<h1 style="color: #2c3e50; text-align: center;">Page 1</h1>...""",
            """<h1 style="color: #2c3e50; text-align: center;">Page 2</h1>...""",
            """<h1 style="color: #2c3e50; text-align: center;">Page 3</h1>..."""
        ]
        self.box_choices = {
            "PERSON": False,
            "ORGANIZATION": False,
            "LOC": False,
            "YEARs": False,
            "PERIOD": False
        }
        self.app = None
        self.window = None


    def pagetoIG(self,content):


        num_page = 0
        for page in content.values():
            print(num_page)
            if type(page) != list:
                self.update_page(page_number=num_page, raw_text=page)
                num_page += 1


    def launch_app(self,content,article_id,data_processor=None):
        """Lance l'application graphique"""
        self.data_processor = data_processor
        if QApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()


        startup_dialog = StartupDialog(self.box_choices)
        if startup_dialog.exec():
            # Optionnel : utiliser les réponses si besoin plus tard
            print("Choix utilisateur :", startup_dialog.box_choices)
        self.pagetoIG(content)
        self.window = MultiPageTextApp(article_id, self.pages, data_processor=self.data_processor,controller=self)
        self.window.show()
        self.app.exec()

    def update_page(self, page_number: int, raw_text: str):

        """Met à jour une page sans lancer l'interface"""
        if page_number >= len(self.pages):
            self.pages.append("")

        # Supprimer les mises en forme des mots déjà cochés
        formatted_text = raw_text

        # Met en gras les textes entre ** ** (nombres)
        if self.box_choices["YEARs"]:
            formatted_text = re.sub(
                r'\*\*(.*?)\*\*',
                r'<span style="font-weight: bold;">\1</span>',
                formatted_text
            )
        else :
            formatted_text = re.sub(
                r'\*\*(.*?)\*\*',
                r'<span\1</span>',
                formatted_text
            )


        if self.box_choices["PERIOD"]:
            formatted_text = re.sub(
                r'¦¦(.*?)¦¦',
                r'<span style="font-weight: bold;">\1</span>',
                formatted_text
            )
        else :
            formatted_text = re.sub(
                r'¦¦(.*?)¦¦',
                r'<span\1</span>',
                formatted_text
            )

        # Met en gras et rouge les textes entre ++ ++ (noms)
        if self.box_choices["PERSON"]:
            formatted_text = re.sub(
                r'\+\+(.*?)\+\+',
                r'<span style="font-weight: bold; color: red;">\1</span>',
                formatted_text
            )
        else :
            formatted_text = re.sub(
                r'\+\+(.*?)\+\+',
                r'<span\1</span>',
                formatted_text
            )


        if self.box_choices["LOC"]:
            formatted_text = re.sub(
                r'@@(.*?)@@',
                r'<span style="font-weight: bold; color: blue;">\1</span>',
                formatted_text
            )
        else :
            formatted_text = re.sub(
                r'@@(.*?)@@',
                r'<span\1</span>',
                formatted_text
            )


        if self.box_choices["ORG"]:
            formatted_text = re.sub(
                r'┤┤(.*?)┤┤',
                r'<span style="font-weight: bold; color: green;">\1</span>',
                formatted_text
            )
        else :
            formatted_text = re.sub(
                r'┤┤(.*?)┤┤',
                r'<span\1</span>',
                formatted_text
            )

        # Met en italique les notes entre <ftn> <ftn>
        formatted_text = re.sub(
            r'<ftn>(.*?)<ftn>',
            r'<span style="font-style: italic; font-size: 12px; color: #555;">\1</span>',
            formatted_text,
            flags=re.DOTALL
        )

        # Remplace les retours à la ligne par <br>
        formatted_text = formatted_text.replace(chr(10), "<br>")

        # Enveloppe dans un conteneur HTML
        self.pages[page_number] = f"""
        <div style="font-family: Georgia; font-size: 14px; text-align: justify; padding: 10px;">
            {formatted_text}
        </div>
        """

        # Met à jour l'affichage si interface ouverte




class StartupDialog(QDialog):
    def __init__(self,box_choices):
        super().__init__()
        self.setWindowTitle("Préférences avant le démarrage")
        self.box_choices = box_choices
        self.setFixedSize(400, 250)

        layout = QVBoxLayout(self)

        question = QLabel("Quelles types d'entités nommées veux tu regarder dans ce document?")
        question.setWordWrap(True)
        layout.addWidget(question)

        self.options = {
            "PERSON": QCheckBox("Personnes (en rouge)"),
            "LOC": QCheckBox("Lieux (en bleu)"),
            "ORG": QCheckBox("Organismes (en vert)"),
            "YEARs": QCheckBox("Années (en noir)"),
            "PERIOD": QCheckBox("Périodes (en noir)")
        }

        for checkbox in self.options.values():
            layout.addWidget(checkbox)

        valider_btn = QPushButton("Continuer")
        valider_btn.clicked.connect(self.valider)
        layout.addWidget(valider_btn)

    def valider(self):
        for label, checkbox in self.options.items():
            self.box_choices[label] = checkbox.isChecked()
        self.accept()


class PopUpDialog(QDialog):
    def __init__(self, mot, choices, question,color, checked_words,article_id,parent=None):
        """
        :param mot: Le mot ciblé pour contextualiser la question
        :param choices: Liste de chaînes représentant les choix (ex: ["Clairement Oui", "Plutôt Oui", ...])
        :param question: Texte de la question à afficher
        :param parent: Parent Qt (optionnel)
        """
        super().__init__(parent)
        self.article_id = article_id
        self.color = color
        self.setWindowTitle(f"Choix pour : {mot}")
        self.setFixedSize(350, 150 + 30 * len(choices))
        self.mot = mot
        self.checked_words = checked_words
        self.reponse = None
        self.radio_buttons = []
        self.button_group = QButtonGroup(self)

        layout = QVBoxLayout(self)
        label = QLabel(f"{question} « {mot} » ?")
        layout.addWidget(label)

        # Crée dynamiquement les boutons radio
        for i, choice in enumerate(choices):
            radio = QRadioButton(choice)
            self.radio_buttons.append(radio)
            self.button_group.addButton(radio, i)
            layout.addWidget(radio)

        valider_btn = QPushButton("Valider")
        valider_btn.clicked.connect(self.valider)
        layout.addWidget(valider_btn)

    def valider(self):
        selected_id = self.button_group.checkedId()
        if selected_id != -1:
            if self.color =="#000000" :
                update_pertinence(self.article_id,self.mot,"highlight",self.radio_buttons[selected_id].text())
            else :
                update_pertinence(self.article_id,self.mot,"highlight",self.radio_buttons[selected_id].text())

        self.accept()



class AddWordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un mot")
        print("1")
        layout = QVBoxLayout()

        # Champ mot
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Mot :"))
        self.word_input = QLineEdit()
        word_layout.addWidget(self.word_input)
        layout.addLayout(word_layout)
        print("1")
        # Champ catégorie
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Catégorie :"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["LOC", "PERSON", "ORG", "Number", "Period"])
        cat_layout.addWidget(self.category_combo)
        layout.addLayout(cat_layout)
        print("1")
        # Boutons OK / Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.add_word)
        layout.addWidget(buttons)
        print("1")
        self.setLayout(layout)

    def reject(self):
        """Ferme simplement la popup quand on clique sur Annuler"""
        self.close()


    def add_word(self):
        word = self.word_input.text().strip()
        category = self.category_combo.currentText()

        if not word or not article_id:
            print("⚠ Aucun mot ou article sélectionné.")
            return

        # Appeler le contrôleur (qui lui-même insère en base)
        print(f"✅ Mot ajouté : {word} ({category}) dans article {article_id}")
        insert_item(article_id, word,category,"Manuellement")
        self.word_input.clear()

    def get_data(self):
        """Renvoie le mot et la catégorie choisis"""
        return self.word_input.text(), self.category_combo.currentText()

class HoverTextEdit(QTextEdit):
    def __init__(self,pages,article_id,current_pages, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reponses_utilisateur = {}  # Pour stocker les réponses
        self.pages = pages
        self.current_pages = current_pages
        self.article_id = article_id


    def remplacer_balise(self, mot, nouveau_html):
        """Remplace la balise contenant le mot par un nouveau fragment HTML"""


        # Attention aux caractères spéciaux HTML : transformer le mot cliqué
        mot_echappe = re.escape(mot)
        print("DEBUT Remplacer Balise")
        # Trouver le span autour du mot exact
        compteur=0
        for i, page in enumerate(self.pages):
            compteur+=1
            print(page)

            print("-------------------------------------------------")
            print(mot_echappe)
            pattern = rf'<span[^>]*?>\s*{mot_echappe}\s*</span>'
            nouveau_contenu, n = re.subn(pattern, nouveau_html, page)

            if n > 0:
                self.pages[i]=nouveau_contenu
                print(compteur)
                print(f"✅ Remplacé '{mot}' par : {nouveau_html}")
            else:
                print(compteur)
                print(f"❌ Impossible de remplacer : '{mot}' (non trouvé dans une balise span)")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.position().toPoint())
            cursor.select(cursor.SelectionType.WordUnderCursor)
            word = cursor.selectedText().strip()

            char_format = cursor.charFormat()
            is_bold = char_format.fontWeight() == QFont.Weight.Bold
            color = char_format.foreground().color().name().lower()  # couleur en hexadécimal

            if is_bold and word not in self.reponses_utilisateur:
                # Choix en fonction de la couleur
                if color == "#ff0000":  # rouge
                    question = "Cette personne est elle pertinente à relever dans l'article"
                    choices = ["Oui c'est un personnage historique important", "Oui c'est un historien ou auteur important","Non"]
                elif color == "#0000ff":  # bleu
                    question = "Ce lieu est-il pertinent dans le contexte de l'article ?"
                    choices = ["Oui", "Non"]
                elif color == "#008000":  # vert
                    question = "Est-ce un personnage important dans cet article ?"
                    choices = ["Oui c'est un personnage lié à des faits historique important dans l'article", "Oui c'est une personne lié à l'article importante", "Non"]
                elif color == "#000000":  # noir
                    question = "Cette année/période historique est elle pertinente pour cette article"
                    choices = ["Oui car elle concerne des faits historiques importants", "Oui car elle est liée à la création de cette article", "Non"]
                else:
                    question = "Voulez-vous annoter ce mot ?"
                    choices = ["Oui", "Non"]

                # Afficher la PopUpDialog
                dialog = PopUpDialog(
                    word,

                    choices=choices,
                    question=question,
                    color=color,
                    checked_words =self.reponses_utilisateur,
                    article_id= self.article_id,
                )

                if dialog.exec():
                    print(f"Réponse pour '{word}' : {dialog.reponse}")
                    self.remplacer_balise(word, f'<span style="color: gray;">{word}</span>')

        # Appelle l'événement standard
        super().mousePressEvent(event)


if __name__ == "__main__":
    controller = TextAppController()
    article_id=1592
    # Modifier les pages sans lancer l'interface

    # Lancer l'interface quand vous le souhaitez
    controller.launch_app(get_article_pages(article_id),article_id,data_processor=None)

