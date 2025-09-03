import subprocess
import sys

def install_requirements(requirements_file="requirements.txt"):
    """
    Installe tous les packages listés dans le fichier requirements.txt
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        print("✅ Tous les packages ont été installés avec succès !")
    except subprocess.CalledProcessError as e:
        print("❌ Erreur lors de l'installation des packages :", e)

if __name__ == "__main__":
    install_requirements()
