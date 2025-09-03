import pyautogui
import time

def get_cursor_position(delay=3):
    """Affiche la position du curseur après un délai en secondes"""
    print(f"Place ton curseur à l'endroit souhaité dans {delay} secondes...")
    time.sleep(delay)
    x, y = pyautogui.position()
    print(f"Position du curseur : X={x}, Y={y}")
    return x, y

# Exemple d'utilisation
if __name__ == "__main__":
    get_cursor_position()