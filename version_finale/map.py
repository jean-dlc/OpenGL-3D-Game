import numpy as np
import ctypes
from OpenGL.GL import *
import pyrr

# Fonction pour générer les sommets et indices d'un cube (8 sommets, 6 faces)
def generate_cube():
    vertices = [
        # Face avant
        -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,  0.0, 0.0,
         0.5, -0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 0.0,
         0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  0.0, 1.0,
        # Face arrière
        -0.5, -0.5, -0.5,  0.0, 0.0, -1.0,  0.0, 0.0,
         0.5, -0.5, -0.5,  0.0, 0.0, -1.0,  1.0, 0.0,
         0.5,  0.5, -0.5,  0.0, 0.0, -1.0,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 0.0, -1.0,  0.0, 1.0,
        
    ]
    indices = []
    for i in range(6):
        base = i * 4
        indices.extend([
            base, base + 1, base + 2,
            base, base + 2, base + 3
        ])
    return vertices, indices

# Fonction pour générer une sphère (utile pour les obstacles)
def generate_sphere(radius=0.5, sectors=20, stacks=20):
    vertices = []
    indices = []
    for i in range(stacks + 1):
        V = i / stacks
        phi = V * np.pi
        for j in range(sectors + 1):
            U = j / sectors
            theta = U * 2 * np.pi
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.cos(phi)
            z = radius * np.sin(phi) * np.sin(theta)
            nx = x / radius
            ny = y / radius
            nz = z / radius
            r = (x + radius) / (2 * radius)
            g = (y + radius) / (2 * radius)
            b = (z + radius) / (2 * radius)
            s = U
            t = V
            vertices.extend([x, y, z, nx, ny, nz, r, g, b, s, t])
    for i in range(stacks):
        for j in range(sectors):
            first = i * (sectors + 1) + j
            second = first + sectors + 1
            indices.extend([
                first, second, first + 1,
                second, second + 1, first + 1
            ])
    return vertices, indices

# Classe Mesh pour gérer les buffers OpenGL d'un objet 3D (cube, sol, etc.)
class Mesh:
    def __init__(self, vertices, indices):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)
        # Création des buffers OpenGL (VAO, VBO, EBO)
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)
        # Liaison des buffers
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        # Attributs de sommet (position, normal, couleur, texcoords)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 11 * 4, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 11 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 11 * 4, ctypes.c_void_p(6 * 4))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, 11 * 4, ctypes.c_void_p(9 * 4))
        glEnableVertexAttribArray(3)
    def draw(self):
        # Dessine le mesh avec OpenGL
        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

# Classe principale pour gérer la carte du jeu (plateformes, murs, rebords, zones)
class GameMap:
    def __init__(self):
        self.platforms = []  # Liste des blocs plateformes
        self.murs = []       # Liste des murs
        self.start_rebord = []  # Rebords de la zone de départ
        self.end_rebord = []    # Rebords de la zone d'arrivée
        # Plateforme de départ (spawn)
        y = 6.5
        x0 = 0
        z0 = 0
        largeur = 10
        longueur = 10
        # Plateforme 2 (arrivée)
        x1 = 0
        z1 = 100
       
        # Position de spawn du joueur (au centre de la plateforme de départ)
        self.spawn = np.array([x0+largeur//2, y+1, z0+2], dtype=np.float32)
        # Définition des zones de départ et d'arrivée (4 blocs centraux sur chaque plateforme)
        self.start_line = {
            'x_min': x0 + largeur//2 - 2,
            'x_max': x0 + largeur//2 + 2,
            'z_min': z0 + longueur - 1,
            'z_max': z0 + longueur + 1
        }
        self.end_line = {
            'x_min': x1 + largeur//2 - 2,
            'x_max': x1 + largeur//2 + 2,
            'z_min': z1 - 1,
            'z_max': z1 + 1
        }
        #  REBORD SPAWN -
        rebord_y = y  # hauteur plateforme
        self.rebord_y = rebord_y  # stocké pour les vérifications
        rebord_z = z0+longueur
        rebord_x_min = self.start_line['x_min']
        rebord_x_max = self.start_line['x_max']
        self.start_rebord = []
        for x in range(rebord_x_min, rebord_x_max):
            pos = np.array([x, rebord_y, rebord_z])
            self.start_rebord.append(pos)
            self.platforms.append(pos)
        # Nouvelle zone de départ : exactement les 4 cubes du rebord
        self.start_line = {
            'x_min': rebord_x_min,
            'x_max': rebord_x_max,
            'z_min': rebord_z,
            'z_max': rebord_z+1
        }
        #  REBORD ARRIVEE 
        end_rebord_y = y  # hauteur plateforme
        end_rebord_z = z1 - 1  # rebord côté spawn
        end_rebord_x_min = self.end_line['x_min']
        end_rebord_x_max = self.end_line['x_max']
        self.end_rebord = []
        for x in range(end_rebord_x_min, end_rebord_x_max):
            pos = np.array([x, end_rebord_y, end_rebord_z])
            self.end_rebord.append(pos)
            self.platforms.append(pos)
        # Nouvelle zone d'arrivée : exactement les 4 cubes du rebord
        self.end_line = {
            'x_min': end_rebord_x_min,
            'x_max': end_rebord_x_max,
            'z_min': end_rebord_z,
            'z_max': end_rebord_z+1
        }
        # Création du mesh du sol (plane_mesh)
        plane_vertices = [
            -100.0, 0.0, -100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  0.0, 0.0,
             100.0, 0.0, -100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  10.0, 0.0,
             100.0, 0.0,  100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  10.0, 10.0,
            -100.0, 0.0,  100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  0.0, 10.0
        ]
        plane_indices = [0, 1, 2, 0, 2, 3]
        self.plane_mesh = Mesh(plane_vertices, plane_indices)

    def draw(self, shader_program, cube_mesh):
        # Dessine toutes les plateformes, murs et rebords (utilise le mesh cube)
        model_loc = glGetUniformLocation(shader_program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, pyrr.matrix44.create_identity())
        # self.plane_mesh.draw()  # Sol gris supprimé
        for plat in self.platforms:
            model_platform = pyrr.matrix44.create_from_translation(plat)
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_platform)
            cube_mesh.draw()
      
        for rebord in self.start_rebord:
            model_rebord = pyrr.matrix44.create_from_translation(rebord)
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_rebord)
            cube_mesh.draw()
        for rebord in self.end_rebord:
            model_rebord = pyrr.matrix44.create_from_translation(rebord)
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_rebord)
            cube_mesh.draw()

    def is_in_start_zone(self, pos):
        # Vérifie si la position est sur un des 4 cubes du rebord (zone de départ)
        
        return (
            self.start_line['x_min'] <= pos[0] < self.start_line['x_max'] and
            self.start_line['z_min'] <= pos[2] < self.start_line['z_max']
        )

    def is_in_end_zone(self, pos):
        # Vérifie si la position est sur un des 4 cubes du rebord (zone d'arrivée)
       
        return (
            self.end_line['x_min'] <= pos[0] < self.end_line['x_max'] and
            self.end_line['z_min'] <= pos[2] < self.end_line['z_max']
        )

    def is_on_platform(self, pos, velocity_y):
        """Vérifie si une position est sur une plateforme"""
        # Position du bas de la sphère
        bottom = pos[1] - 0.5  
        # Vérification pour chaque plateforme
        for plat in self.platforms:
            plat_top = plat[1] + 0.5  # Haut de la plateforme
            diff = bottom - plat_top
            # Si proche du haut de la plateforme et à l'intérieur des limites X/Z
            if (abs(diff) < 0.1 and  # Tolérance verticale
                abs(pos[0] - plat[0]) < 0.7 and  # Marge X
                abs(pos[2] - plat[2]) < 0.7 and  # Marge Z
                velocity_y <= 0):  # En descente ou stationnaire
                return True
        return False

    def afficher_texte(self, texte):
        """
        Affiche un texte simple en haut de l'écran (OpenGL, version basique)
        ATTENTION : glWindowPos2f et glDrawPixels ne sont pas supportés en OpenGL Core Profile (GLFW 3.3+)
        Donc ici, on affiche juste dans la console pour éviter le crash.
        Pour un vrai overlay, il faudra une autre méthode (texture + quad 2D).
        """
        print(texte)  # Affichage console temporaire, évite le crash OpenGL


