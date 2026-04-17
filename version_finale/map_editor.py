import json
import numpy as np

class MapEditor:
    def __init__(self, platforms=None):
        # Initialise l'éditeur de carte avec une liste de plateformes, blocs
        self.platforms = platforms if platforms is not None else []
        self.edit_mode = False  # Mode édition activé ou non
        # Position du curseur d'édition, cube virtuel, pour ajouter/supprimer des blocs
        self.cursor_pos = np.array([0, 2, 0], dtype=float)
        self.cursor_speed = 0.2  # Vitesse de déplacement du curseur, c'est pas très rapide

    def toggle_edit_mode(self):
        # Active ou désactive le mode édition, ajout/suppression de blocs
        self.edit_mode = not self.edit_mode
        print(f"Mode édition: {'ON' if self.edit_mode else 'OFF'}")
        if self.edit_mode:
            print("Mouvement libre activé : ZQSD pour X/Z, A/E pour Y")

    def move_cursor(self, direction):
        # Déplace le curseur d'édition dans la direction donnée, tableau numpy
        self.cursor_pos += direction * self.cursor_speed
        print(f"Curseur déplacé: {self.cursor_pos}")

    def set_cursor(self, pos):
        # Place le curseur à une position précise, utile pour TP le curseur
        self.cursor_pos = np.array(pos, dtype=float)

    def get_cursor(self):
        # Retourne la position actuelle du curseur, copie pour éviter les bugs
        return self.cursor_pos.copy()

    def add_block(self, pos=None):
        # Ajoute un bloc à la position donnée ou à la position du curseur si rien n'est précisé
        if pos is None:
            pos = self.cursor_pos
        pos = np.round(pos).astype(int)
        if not any(np.array_equal(pos, p) for p in self.platforms):
            self.platforms.append(pos)
            print(f"Bloc ajouté: {pos}")

    def remove_block(self, pos=None):
        # Supprime un bloc à la position donnée ou à la position du curseur
        if pos is None:
            pos = self.cursor_pos
        pos = np.round(pos).astype(int)
        for i, p in enumerate(self.platforms):
            if np.array_equal(pos, p):
                del self.platforms[i]
                print(f"Bloc supprimé: {pos}")
                break

    def save(self, filename="map_custom.json"):
        # Sauvegarde la liste des blocs dans un fichier json, par défaut map_custom.json
        data = [p.tolist() for p in self.platforms]
        with open(filename, "w") as f:
            json.dump(data, f)
        print(f"Map sauvegardée dans {filename}")

    def load(self, filename="map_custom.json"):
        # Charge une liste de blocs depuis un fichier json, remplace la carte courante
        with open(filename, "r") as f:
            data = json.load(f)
        self.platforms = [np.array(p) for p in data]
        print(f"Map chargée depuis {filename}")

    def handle_key(self, key):
        # Gère les touches pour déplacer le curseur en mode édition : ZQSD, A, W
        if not self.edit_mode:
            return
        if key == 90:  # Z
            self.move_cursor(np.array([0, 0, -1]))
        elif key == 83:  # S
            self.move_cursor(np.array([0, 0, 1]))
        elif key == 81:  # Q
            self.move_cursor(np.array([-1, 0, 0]))
        elif key == 68:  # D
            self.move_cursor(np.array([1, 0, 0]))
        elif key == 65:  # A
            self.move_cursor(np.array([0, 1, 0]))
        elif key == 87:  # W
            self.move_cursor(np.array([0, -1, 0]))
