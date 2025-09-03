import sys

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QApplication

from src.database.db_insert import *
from src.database.db_query import *


class SearchWordWidget(QWidget):
    """Petite maquette d'une application qui permettrait de rechercher des mots dans la BDD en fonction de certains critères
    et qui renverrait les articles dans laquelle le mot est présent (date, personne ,...)
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recherche de mot")
        self.resize(500, 400)

        layout = QVBoxLayout()

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.input_word = QLineEdit()
        self.input_word.setPlaceholderText("Tapez un mot...")
        self.search_button = QPushButton("Rechercher")
        self.search_button.clicked.connect(self.search_word)
        search_layout.addWidget(self.input_word)
        search_layout.addWidget(self.search_button)

        # Zone de résultats
        self.results = QTextEdit()
        self.results.setReadOnly(True)

        layout.addLayout(search_layout)
        layout.addWidget(QLabel("Résultats :"))
        layout.addWidget(self.results)

        self.setLayout(layout)

    def search_word(self):

        word = self.input_word.text().strip()
        if not word:
            self.results.setText("⚠ Veuillez entrer un mot.")

            return

        results = search_word_in_db(word)

        if not results:
            self.results.setText(f"❌ Aucun résultat pour « {word} »")

        else:

            text = f"Résultats pour « {word} » :\n\n"
            for  article_id in results:
                text += f"📄 Article {article_id} \n"

            self.results.setText(text)

if __name__ == "__main__":
    app = QApplication([])
    window = SearchWordWidget()
    window.show()
    sys.exit(app.exec())