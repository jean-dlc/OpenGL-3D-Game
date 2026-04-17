#!/usr/bin/env python3

# Fichier principal du jeu 3D (plateforme/parkour)
# Contient la boucle principale, la gestion du joueur, de la caméra, du décor et de l'éditeur de map

import OpenGL.GL as GL
import glfw
import numpy as np
import os
import ctypes
from add import Shader
import pyrr
from map import GameMap  # Import de GameMap
from map_editor import MapEditor
import json

# Fonction utilitaire pour générer un cube (sommets et indices)
def generate_cube():
    vertices = [
        # Front face
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0, 0.0,  0.0, 0.0,  # Bottom-left
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0, 0.0,  1.0, 0.0,  # Bottom-right
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0, 0.0,  1.0, 1.0,  # Top-right
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0, 0.0, 0.0,  0.0, 1.0,  # Top-left
        
        # Back face
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, 0.0,  0.0, 0.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, 0.0,  1.0, 0.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, 0.0,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0, 0.0,  0.0, 1.0,
        
        # Top face
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0, 1.0,  0.0, 0.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 0.0, 1.0,  1.0, 0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0, 1.0,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0, 1.0,  0.0, 1.0,
        
        # Bottom face
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0, 0.0,  0.0, 0.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0, 0.0,  1.0, 0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 1.0, 0.0,  1.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 1.0, 0.0,  0.0, 1.0,
        
        # Right face
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0, 1.0,  0.0, 0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0, 1.0,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0, 1.0,  1.0, 1.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 1.0, 1.0,  0.0, 1.0,
        
        # Left face
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 0.0, 1.0,  0.0, 0.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 0.0, 1.0,  1.0, 0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0, 1.0,  1.0, 1.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0, 1.0,  0.0, 1.0
    ]
    
    indices = []
    for i in range(6):  # 6 faces
        base = i * 4
        indices.extend([
            base, base + 1, base + 2,  # Premier triangle
            base, base + 2, base + 3   # Deuxième triangle
        ])
    
    return vertices, indices

# Fonction utilitaire pour générer une sphère (pour les obstacles)
def generate_sphere(radius=0.5, sectors=20, stacks=20):
    vertices = []
    indices = []
    # Génère les sommets de la sphère (centrée en 0,0,0)
    for i in range(stacks + 1):
        V = i / stacks
        phi = V * np.pi
        for j in range(sectors + 1):
            U = j / sectors
            theta = U * 2 * np.pi
            # Position du sommet
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.cos(phi)
            z = radius * np.sin(phi) * np.sin(theta)
            # Vecteur normal (pour l'éclairage)
            nx = x / radius
            ny = y / radius
            nz = z / radius
            # Couleur (dépend de la position)
            r = (x + radius) / (2 * radius)
            g = (y + radius) / (2 * radius)
            b = (z + radius) / (2 * radius)
            # Coordonnées de texture
            s = U
            t = V
            vertices.extend([x, y, z, nx, ny, nz, r, g, b, s, t])
    # Génère les indices pour les triangles
    for i in range(stacks):
        for j in range(sectors):
            first = i * (sectors + 1) + j
            second = first + sectors + 1
            indices.extend([
                first, second, first + 1,
                second, second + 1, first + 1
            ])
    return vertices, indices


class Mesh:
    def __init__(self, vertices, indices):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)
        
        # Création des buffers
        self.VAO = GL.glGenVertexArrays(1)
        self.VBO = GL.glGenBuffers(1)
        self.EBO = GL.glGenBuffers(1)
        
        # Liaison des buffers
        GL.glBindVertexArray(self.VAO)
        
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL.GL_STATIC_DRAW)
        
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL.GL_STATIC_DRAW)
        
        # Position attribute (3 floats)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 11 * 4, None)
        GL.glEnableVertexAttribArray(0)
        
        # Normal attribute (3 floats)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 11 * 4, ctypes.c_void_p(3 * 4))
        GL.glEnableVertexAttribArray(1)
        
        # Color attribute (3 floats)
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, GL.GL_FALSE, 11 * 4, ctypes.c_void_p(6 * 4))
        GL.glEnableVertexAttribArray(2)
        
        # Texture coords attribute (2 floats)
        GL.glVertexAttribPointer(3, 2, GL.GL_FLOAT, GL.GL_FALSE, 11 * 4, ctypes.c_void_p(9 * 4))
        GL.glEnableVertexAttribArray(3)
    
    def draw(self):
        GL.glBindVertexArray(self.VAO)
        GL.glDrawElements(GL.GL_TRIANGLES, len(self.indices), GL.GL_UNSIGNED_INT, None)

class Game:
    def __init__(self):
        self.window = self.init_window()
        self.init_context()
        self.init_shaders()
        # Initialisation de la carte AVANT les meshes
        self.game_map = GameMap()
        # Chargement automatique de map.json si présent 
        try:
            with open("version_finale/map.json", "r") as f:
                data = json.load(f)
            self.game_map.platforms = [np.array(p) for p in data]
            print(f"Carte map.json chargée au démarrage : {len(self.game_map.platforms)} blocs")
        except Exception as e:
            print(f"Pas de map.json ou erreur de chargement : {e}")
        self.init_meshes()
        self.init_camera()
        
        # Position initiale du joueur (sur la plateforme de spawn)
        self.cube_pos = self.game_map.spawn.copy()
        self.cube_rotation = 0.0
        self.base_speed = 0.6  # vitesse de base augmentée
        self.sprint_speed = 0.8  # vitesse sprint augmentée
        self.cube_speed = self.base_speed
        self.cube_velocity_y = 0.0
        self.jump_power = 0.36  # nouvelle variable pour la hauteur de saut
        self.gravity = -0.04  # gravité encore augmentée (valeur précédente : -0.001)
        self.on_ground = True
        self.camera_distance = 6.0
        self.camera_height = 1.0
        
        # Chronomètre
        self.chrono_started = False
        self.chrono_start_time = 0.0
        self.chrono_end_time = 0.0
        
        self.sprinting = False
        # Initialisation de l'éditeur de map
        self.map_editor = MapEditor([p.copy() for p in self.game_map.platforms])
        # Mode déplacement libre (toggle avec N)
        self.free_move_mode = False
        
    def init_window(self):
        if not glfw.init():
            raise Exception("GLFW initialization failed")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        monitor = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(monitor)
        window = glfw.create_window(mode.size.width, mode.size.height, "OpenGL Project", monitor, None)
        if not window:
            glfw.terminate()
            raise Exception("Window creation failed")
        glfw.make_context_current(window)
        glfw.set_key_callback(window, self.key_callback)
        glfw.set_cursor_pos_callback(window, self.mouse_callback)
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        return window
        
    def init_context(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.2, 0.3, 0.3, 1.0)
        
    def init_shaders(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        vs_path = os.path.join(current_dir, "shader.vert")
        fs_path = os.path.join(current_dir, "shader.frag")
        
        self.shader_program = Shader.create_program_from_file(vs_path, fs_path)
        if not self.shader_program:
            raise Exception("Failed to create shader program")
            
    def init_meshes(self):
        plane_vertices = [
            -100.0, 0.0, -100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  0.0, 0.0,
             100.0, 0.0, -100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  10.0, 0.0,
             100.0, 0.0,  100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  10.0, 10.0,
            -100.0, 0.0,  100.0,  0.0, 1.0, 0.0,  1.0, 1.0, 1.0,  0.0, 10.0
        ]
        plane_indices = [0, 1, 2, 0, 2, 3]
        self.plane = Mesh(plane_vertices, plane_indices)
        # Création d'une sphère pour le joueur
        sphere_vertices, sphere_indices = generate_sphere(radius=0.5, sectors=32, stacks=32)
        self.player_sphere = Mesh(sphere_vertices, sphere_indices)
        # self.sphere = Mesh(sphere_vertices, sphere_indices)  # SUPPRIMÉ : plus d'obstacle sphère
        self.cube_vertices, self.cube_indices = generate_cube()
        self.cube = Mesh(self.cube_vertices, self.cube_indices)
        # Suppression de la création des meshes décor (start_line_mesh, end_line_mesh, teleport_mesh)
        
    def init_camera(self):
        self.camera_pos = np.array([0.0, 2.0, 5.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.camera_speed = 0.1
        
        # Variables pour la rotation de la caméra
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_x = 400
        self.last_y = 300
        self.first_mouse = True
        self.mouse_sensitivity = 0.1
        
    def mouse_callback(self, window, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False
        
        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x = xpos
        self.last_y = ypos
        
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity
        
        self.yaw += xoffset
        self.pitch += yoffset
        
        if self.pitch > 40.0:
            self.pitch = 40.0
        if self.pitch < -40.0:
            self.pitch = -40.0
            
        front = np.array([
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        ])
        self.camera_front = front / np.linalg.norm(front)
        
    def is_on_support(self, pos, velocity_y):
        # Test sol
        if abs((pos[1] - 0.5) - 0.0) < 0.1 and velocity_y <= 0:
            return True
        # Test plateformes (délégué à GameMap)
        return self.game_map.is_on_platform(pos, velocity_y)

    def key_callback(self, window, key, scancode, action, mods):
        # print(f"Key event: key={key}, action={action}, edit_mode={self.map_editor.edit_mode}, free_move={self.free_move_mode}")
        if not hasattr(self, 'pressed_keys'):
            self.pressed_keys = set()
        if action == glfw.PRESS:
            self.pressed_keys.add(key)
            # Mode déplacement libre toggle (N = 78)
            if key == 78:
                self.free_move_mode = not self.free_move_mode
                print(f"Mode déplacement libre : {'activé' if self.free_move_mode else 'désactivé'} (touche N)")
            # Mode édition toggle (utilise le code 59 pour 'M' sur ton clavier)
            if key == 59:
                self.map_editor.toggle_edit_mode()
                print("Mode édition togglé avec la touche code 59 (M sur ton clavier)")
            # Ajouter un bloc (E)
            if key == 69 and self.map_editor.edit_mode:
                self.map_editor.add_block(self.cube_pos)
                self.game_map.platforms = [p.copy() for p in self.map_editor.platforms]
            # Supprimer un bloc (R)
            if key == 82 and self.map_editor.edit_mode:
                self.map_editor.remove_block(self.cube_pos)
                self.game_map.platforms = [p.copy() for p in self.map_editor.platforms]
            # Sauvegarder (P)
            if key == 80 and self.map_editor.edit_mode:
                self.map_editor.save()
            # Charger (L)
            if key == 76 and self.map_editor.edit_mode:
                self.map_editor.load()
                self.game_map.platforms = [p.copy() for p in self.map_editor.platforms]
        elif action == glfw.RELEASE:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
            if key == glfw.KEY_LEFT_CONTROL or key == glfw.KEY_RIGHT_CONTROL:
                self.sprinting = False
                self.cube_speed = self.base_speed
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        # Saut (uniquement si le cube est sur le sol ou une plateforme)
        if key == glfw.KEY_SPACE and action == glfw.PRESS:
            if self.is_on_support(self.cube_pos, self.cube_velocity_y):
                self.cube_velocity_y = self.jump_power  # utilise la nouvelle hauteur de saut
                self.on_ground = False
        # Déclenchement manuel du chrono avec Entrée dans la zone de départ
        if key == glfw.KEY_ENTER and action == glfw.PRESS:
            if (not self.chrono_started and
                self.game_map.is_in_start_zone(self.cube_pos)):
                self.start_triggered = True

    def compute_movement(self):
        if not hasattr(self, 'pressed_keys'):
            self.pressed_keys = set()
        move = np.zeros(3, dtype=np.float32)
        if self.free_move_mode:
          # Mode déplacement libre : W/A/S/D pour X/Z, Q pour monter, Z pour descendre
            # W = 87, A = 65, S = 83, D = 68, Q = 81, Z = 90
            forward = np.array([
                np.cos(np.radians(self.yaw)),
                0,
                np.sin(np.radians(self.yaw))
            ])
            right = np.cross(forward, np.array([0, 1, 0]))
            if 87 in self.pressed_keys:  # W
                move += forward
            if 83 in self.pressed_keys:  # S
                move -= forward
            if 65 in self.pressed_keys:  # A
                move -= right
            if 68 in self.pressed_keys:  # D
                move += right
            if 81 in self.pressed_keys:  # Q
                move[1] += 1  # Monter
            if 90 in self.pressed_keys:  # Z
                move[1] -= 1  # Descendre
        else:
            # Mode normal : W/A/S/D
            forward = np.array([
                np.cos(np.radians(self.yaw)),
                0,
                np.sin(np.radians(self.yaw))
            ])
            right = np.cross(forward, np.array([0, 1, 0]))
            if glfw.KEY_W in self.pressed_keys:
                move += forward
            if glfw.KEY_S in self.pressed_keys:
                move -= forward
            if glfw.KEY_A in self.pressed_keys:
                move -= right
            if glfw.KEY_D in self.pressed_keys:
                move += right
        if np.linalg.norm(move) > 0:
            move = move / np.linalg.norm(move) * self.cube_speed
            if self.free_move_mode:
                self.cube_pos += move
            else:
                next_pos = self.check_collisions(self.cube_pos + move)
                self.cube_pos = next_pos
            # Met à jour la rotation du cube pour suivre la direction
            self.cube_rotation = np.degrees(np.arctan2(move[2], move[0]))

    def update_camera(self):
        # Calcul direction caméra selon yaw/pitch
        direction = np.array([
            np.cos(np.radians(self.pitch)) * np.cos(np.radians(self.yaw)),
            np.sin(np.radians(self.pitch)),
            np.cos(np.radians(self.pitch)) * np.sin(np.radians(self.yaw))
        ])
        direction = direction / np.linalg.norm(direction)
        # Position caméra derrière le cube
        self.camera_pos = self.cube_pos - direction * self.camera_distance
        self.camera_pos[1] = self.cube_pos[1] + self.camera_height
        self.camera_front = self.cube_pos - self.camera_pos
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        
    def check_collisions(self, next_pos):
        # Correction : gestion séparée des axes pour éviter de s'enfoncer dans les cubes
        pos = self.cube_pos.copy()
        # Test X
        test_pos = pos.copy()
        test_pos[0] = next_pos[0]
        for plat in self.game_map.platforms:
            min_cube = test_pos - 0.5
            max_cube = test_pos + 0.5
            min_plat = plat - 0.5
            max_plat = plat + 0.5
            overlap = (
                min_cube[0] < max_plat[0] and max_cube[0] > min_plat[0] and
                min_cube[1] < max_plat[1] and max_cube[1] > min_plat[1] and
                min_cube[2] < max_plat[2] and max_cube[2] > min_plat[2]
            )
            if overlap:
                test_pos[0] = pos[0]
                break
        
        # Test Z
        test_pos2 = test_pos.copy()
        test_pos2[2] = next_pos[2]
        for plat in self.game_map.platforms:
            min_cube = test_pos2 - 0.5
            max_cube = test_pos2 + 0.5
            min_plat = plat - 0.5
            max_plat = plat + 0.5
            overlap = (
                min_cube[0] < max_plat[0] and max_cube[0] > min_plat[0] and
                min_cube[1] < max_plat[1] and max_cube[1] > min_plat[1] and
                min_cube[2] < max_plat[2] and max_cube[2] > min_plat[2]
            )
            if overlap:
                test_pos2[2] = pos[2]
                break
        
        # Test Y (vertical)
        test_pos3 = test_pos2.copy()
        test_pos3[1] = next_pos[1]
        for plat in self.game_map.platforms:
            min_cube = test_pos3 - 0.5
            max_cube = test_pos3 + 0.5
            min_plat = plat - 0.5
            max_plat = plat + 0.5
            overlap = (
                min_cube[0] < max_plat[0] and max_cube[0] > min_plat[0] and
                min_cube[1] < max_plat[1] and max_cube[1] > min_plat[1] and
                min_cube[2] < max_plat[2] and max_cube[2] > min_plat[2]
            )
            if overlap:
                if pos[1] >= plat[1]:
                    test_pos3[1] = plat[1] + 1.0
                else:
                    test_pos3[1] = pos[1]
                break
                
        # Collision sol (y=0)
        if test_pos3[1] < 0.5:
            test_pos3[1] = 0.5
            
        return test_pos3

    def apply_gravity(self):
        # Appliquer la gravité
        self.cube_velocity_y += self.gravity
        self.cube_pos[1] += self.cube_velocity_y
        
    def check_chrono_and_arrival(self):
        # Démarrage automatique du chrono dans la zone de départ
        if not self.chrono_started and self.chrono_end_time == 0.0:
            if self.game_map.is_in_start_zone(self.cube_pos):
                self.chrono_started = True
                self.chrono_start_time = glfw.get_time()
                print('Chronomètre lancé !')
                
        # Arrêt du chrono si dans la zone d'arrivée
        if self.chrono_started and self.chrono_end_time == 0.0:
            if self.game_map.is_in_end_zone(self.cube_pos):
                self.chrono_end_time = glfw.get_time()
                chrono = self.chrono_end_time - self.chrono_start_time
                print(f'Arrivée ! Temps : {chrono:.2f} secondes')
                self.chrono_started = False
                self.chrono_end_time = 0.0

    def run(self):
        while not glfw.window_should_close(self.window):
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            if not self.free_move_mode:
                # 1. Calcul du mouvement horizontal (WASD)
                self.compute_movement()
                # 2. Appliquer la gravité
                self.cube_velocity_y += self.gravity
                # 3. Appliquer le mouvement vertical
                next_pos = self.cube_pos.copy()
                next_pos[1] += self.cube_velocity_y
                # 4. Collision sur tous les axes
                after_gravity = self.check_collisions(next_pos)
                # 5. Détection de l'état au sol
                on_any_surface = self.is_on_support(after_gravity, self.cube_velocity_y)
                if on_any_surface:
                    if self.cube_velocity_y < 0:
                        self.cube_velocity_y = 0
                    self.on_ground = True
                else:
                    self.on_ground = False
                self.cube_pos = after_gravity
            else:
                # En mode déplacement libre, pas de gravité ni de collision verticale
                self.compute_movement()
            self.check_chrono_and_arrival()
            self.update_camera()
            
            # Matrices de vue et projection
            view = pyrr.matrix44.create_look_at(
                self.camera_pos,
                self.cube_pos,
                self.camera_up
            )
            
            width, height = glfw.get_framebuffer_size(self.window)
            if width == 0: width = 1
            if height == 0: height = 1
            projection = pyrr.matrix44.create_perspective_projection_matrix(
                45.0, width / height, 0.1, 100.0
            )
            
            # Configuration du shader
            GL.glUseProgram(self.shader_program)
            model_loc = GL.glGetUniformLocation(self.shader_program, "model")
            view_loc = GL.glGetUniformLocation(self.shader_program, "view")
            proj_loc = GL.glGetUniformLocation(self.shader_program, "projection")
            GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view)
            GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, projection)
            
            # Dessin du décor (sol, plateformes, lignes, etc.) via GameMap
            self.game_map.draw(self.shader_program, self.cube)
            
            # Dessin du joueur : maintenant une sphère
            model_player = pyrr.matrix44.create_from_translation(self.cube_pos)
            GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, model_player)
            self.player_sphere.draw()
            
            # TP au spawn si le joueur tombe sous le parkour
            if self.cube_pos[1] <= 1:
                print('Tu es tombé ! Téléportation au spawn.')
                self.cube_pos = self.game_map.spawn.copy()
                self.cube_velocity_y = 0.0
                # Reset chrono
                self.chrono_started = False
                self.chrono_start_time = 0.0
                self.chrono_end_time = 0.0
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()

def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        glfw.terminate()

if __name__ == '__main__':
    main()