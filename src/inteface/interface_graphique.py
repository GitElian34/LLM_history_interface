import re

from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                             QWidget, QPushButton, QHBoxLayout, QToolTip, QDialog, QLabel, QCheckBox, QRadioButton,
                             QButtonGroup, QComboBox, QLineEdit, QDialogButtonBox)
from PyQt6.QtGui import QFont, QTextCharFormat
from PyQt6.QtCore import Qt

from src.database.db_insert import update_pertinence, insert_item, update_etat
from src.database.db_query import get_all_articles, get_article_pages, search_etat_with_article_id


class MultiPageTextApp(QMainWindow):
    """Classe qui va gérer toutes les classes liées à l'affichage et à l'UI et les pages de l'article'"""
    def __init__(self, article_id, pages = None, controller=None):
        super().__init__()

        self.controller = controller        # référence au controller pour permettre de changer d'article
        self.setWindowTitle("Interface Graphique")
        self.resize(800, 600)
        self.article_id = article_id        # numéro de l'Article actuel présenté sur l'interface
        self.current_page = 0               # Page actuelle
        # Contenu des pages sous forme de texte
        self.pages = pages if pages is not None else []
        # Widget central et layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()
        self.article_combo = QComboBox()  #Menu pour sélectionner les articles
        self.article_combo.addItems([(str(a) +" - " +str(search_etat_with_article_id(a))) for a in get_all_articles()])  # liste des articles
        self.article_combo.currentIndexChanged.connect(self.change_selected_article)
        top_layout.addWidget(self.article_combo)
        main_layout.addLayout(top_layout)

        self.article_state_button = QPushButton("Modifier") #Menu pour modifier l'état de complétion de l'article
        self.article_state_button.clicked.connect(self.open_change_state_dialog)

        self.add_button = QPushButton("Ajouter")    #Bouton pour ajouter des mots manquants qui seraient importants dans l'article
        self.add_button.clicked.connect(self.open_add_word_dialog)

        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.article_state_button)


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
        """Permet de switcher entre plusieurs articles présents dans la BDD"""
        selected_text = self.article_combo.currentText()

        # Récupère uniquement l'ID avant le " - "
        article_id = selected_text.split(" - ")[0]

        print(f"Article sélectionné (ID seul) : {article_id}")

        self.article_id = article_id  # stocké en string

        new_article = get_article_pages(article_id)
        self.controller.pagetoIG(new_article)
        self.current_page = 0
        self.display_page()

    def refresh_current_page(self):
        """Recharge la page actuelle en conservant l'article sélectionné par ID"""

        # Sauvegarder l'ID actuel (avant le clear)
        current_text = self.article_combo.currentText()
        current_id = current_text.split(" - ")[0]  # récupère uniquement l’ID avant " - "

        self.article_combo.blockSignals(True)
        self.article_combo.clear()

        # Recharger tous les articles avec leur état
        for a in get_all_articles():
            self.article_combo.addItem(f"{a} - {search_etat_with_article_id(a)}")

        # Retrouver l'index correspondant à l'ID sauvegardé
        for i in range(self.article_combo.count()):
            item_id = self.article_combo.itemText(i).split(" - ")[0]
            if item_id == current_id:
                self.article_combo.setCurrentIndex(i)
                break

        self.article_combo.blockSignals(False)
        self.display_page()

    def display_page(self):
        """Affiche la page actuelle avec le numéro en bas à droite."""
        # Crée un mot de test avec une infobulle (attribut title)
        print(self.pages[self.current_page])

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
        """Créer une instance de la class AddWordDialog lorsque le bouton est cliqué"""
        dialog = AddWordDialog(self.article_id)
        dialog.exec()

    def open_change_state_dialog(self):
        """Créer une instance de la class EtatDialog lorsque le bouton est cliqué"""
        dialog = EtatDialog(self.article_id)
        dialog.exec()

class TextAppController:
    """Classe qui va faire la liaison entre la BDD, les intéraction de l'utilisateur et l'UI"""
    def __init__(self):
        self.pages = [
            # Votre contenu initial des pages ici
            """<h1 style="color: #2c3e50; text-align: center;">Page 1</h1>...""",
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

    def pagetoIG(self, content):
        """Cette fonction prend en argument le contenu issu de la BDD et le transforme pour qu'il
        soit utilisable dans l'interface graphique"""
        num_page = 0
        # Charger le nouveau contenu

        for page in content.values():
            if not isinstance(page, list):  # éviter les listes vides
                self.update_page(page_number=num_page, raw_text=page)
                num_page += 1
        for i in range(len(self.pages) - 1, -1, -1):  # parcours à l'envers pour supprimer les pages en trop restante
            if i >= len(content):
                del self.pages[i]


    def launch_app(self,content,article_id):
        """Lance l'application graphique"""

        if QApplication.instance() is None:
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()


        startup_dialog = StartupDialog(self.box_choices) #
        if startup_dialog.exec():
            # Optionnel : utiliser les réponses si besoin plus tard
            print("Choix utilisateur :", startup_dialog.box_choices)
        self.pagetoIG(content)
        self.window = MultiPageTextApp(article_id, self.pages,controller=self)
        self.window.show()
        self.app.exec()

    def update_page(self, page_number: int, raw_text: str):

        """Met à jour une page sans lancer l'interface
            Va également se charger de transformer les mots mis en avant dans le texte (date, person,...)
            en modifiants leur couleur, leur taille et en les mettants en gras
        """
        if page_number >= len(self.pages):
            self.pages.append("")
            print("new page")

        # Supprimer les mises en forme des mots déjà cochés
        formatted_text = raw_text

        # Met en gras les textes entre ** ** (nombres et entre ¦¦ periodes)
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


class EtatDialog(QDialog):
    """classe qui permet de modifier l'état de complétion de l'article sélectionné"""
    def __init__(self, article_id,parent=None):
        super().__init__(parent)
        self.article_id = article_id
        self.setWindowTitle("Choisir l'état")
        self.setModal(True)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Sélectionnez l'état de l'article :"))

            # Groupe de boutons radio
        self.button_group = QButtonGroup(self)
        self.radio_incomplet = QRadioButton("Incomplet")
        self.radio_encours = QRadioButton("En cours")
        self.radio_complet = QRadioButton("Complet")

        self.button_group.addButton(self.radio_incomplet)
        self.button_group.addButton(self.radio_encours)
        self.button_group.addButton(self.radio_complet)

        layout.addWidget(self.radio_incomplet)
        layout.addWidget(self.radio_encours)
        layout.addWidget(self.radio_complet)

            # Boutons OK/Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                       QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.choice_accepted)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choice_accepted(self):

        update_etat(self.article_id,self.get_choice())

        print(self.article_id)
        self.accept()
    def get_choice(self):

        if self.radio_incomplet.isChecked():
            return "incomplet"
        elif self.radio_encours.isChecked():
            return "en cours"
        elif self.radio_complet.isChecked():
            return "complet"
        return None



class StartupDialog(QDialog):
    """Classe qui permet à l'utilisateur de choisir quel type d'entités nommées il veut mettre en avant dans le texte"""
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
        Classe qui permet lorsqu'un mot highlight (en gras) est cliqué de définir sa pertinence dans l'article

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
        """Mise à jour dans la BDD, highlight étant ici la méthode par défaut
            cela pourrait d'ailleurs poser problème si l'on modifie la méthode d'extraction
            """
        selected_id = self.button_group.checkedId()
        if selected_id != -1:
            if self.color =="#000000" :
                update_pertinence(self.article_id,self.mot,"highlight",self.radio_buttons[selected_id].text())
            else :
                update_pertinence(self.article_id,self.mot,"highlight",self.radio_buttons[selected_id].text())

        self.accept()



class AddWordDialog(QDialog):
    """Classe perméttant à l'utilisateur d'ajouter des mots dans la BDD s'il les pense pertinents pour l'article"""
    def __init__(self, article_id,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un mot")
        layout = QVBoxLayout()

        # Champ mot
        self.article_id = article_id
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Mot :"))
        self.word_input = QLineEdit()
        word_layout.addWidget(self.word_input)
        layout.addLayout(word_layout)

        # Champ catégorie
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Catégorie :"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["LOC", "PERSON", "ORG", "Number", "Period"])
        cat_layout.addWidget(self.category_combo)
        layout.addLayout(cat_layout)

        # Boutons OK / Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.add_word)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def reject(self):
        """Ferme simplement la popup quand on clique sur Annuler"""
        self.close()


    def add_word(self):
        word = self.word_input.text().strip()
        category = self.category_combo.currentText()

        if not word or not self.article_id:
            print("⚠ Aucun mot ou article sélectionné.")
            return

        # Appeler le contrôleur (qui lui-même insère en base)
        print(f"✅ Mot ajouté : {word} ({category}) dans article {self.article_id}")
        insert_item(self.article_id, word,category,"Manuellement")
        self.word_input.clear()

    def get_data(self):
        """Renvoie le mot et la catégorie choisis"""
        return self.word_input.text(), self.category_combo.currentText()

class HoverTextEdit(QTextEdit):
    """classe qui va appeler La classe PopUpdialog pour récupérer le mot qui a été cliqué"""
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
        """fonction qui définit le comportement du programme lorsque l'on clique sur un des mots mis en gras"""
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
    #article_id=1592
    # Modifier les pages sans lancer l'interface
    first_article_id = get_all_articles()[0]
    # Lancer l'interface quand vous le souhaitez
    controller.launch_app(get_article_pages(first_article_id),first_article_id)

