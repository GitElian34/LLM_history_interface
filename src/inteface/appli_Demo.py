import tkinter as tk
from tkinter import messagebox


class SearchApp:
    def __init__(self, root, data):
        self.root = root
        self.root.title("Maquette Recherche")
        self.root.geometry("400x200")
        self.data = data

        # Configuration de la validation
        val_cmd = (self.root.register(self.validate_number), '%P')

        # Création des widgets
        self.label = tk.Label(root, text="Entrez une année :")
        self.label.pack(pady=10)

        self.search_entry = tk.Entry(root, width=40, validate="key", validatecommand=val_cmd)
        self.search_entry.pack(pady=5)

        self.search_button = tk.Button(root, text="Rechercher", command=self.get_search_text)
        self.search_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def validate_number(self, new_value):
        """Valide que la saisie est un nombre entier positif"""
        if new_value == "":
            return True  # Permet de vider le champ
        return new_value.isdigit()

    def year_in_article(self, year:int):
        for cle in self.data:
            if isinstance(cle, tuple):
                if year >= cle[0] and year <= cle[1]:
                    return True
            else:
                if year == cle:
                    return True
        return False
    def get_search_text(self):
        """Récupère le texte saisi et vérifie que c'est un nombre valide"""
        self.search_text = self.search_entry.get()

        if not self.search_text.strip():
            messagebox.showwarning("Attention", "Veuillez entrer une année !")

        try:
            year = int(self.search_text)
            if(self.year_in_article(year)):
               self.result_label.config(text=f"Année : {year} trouvée dans l'article")
            else:
                self.result_label.config(text=f"Année : {year} non présente dans l'article")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre valide")

    def process_text(self, year):
        """Traitement de l'année"""
        print(f"Recherche pour l'année : {year}")
        # Ajoutez ici votre logique de recherche dans self.data


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root, data={})  # Remplacez par vos données réelles
    root.mainloop()