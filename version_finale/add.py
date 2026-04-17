import os
import OpenGL.GL as GL

# Classe utilitaire pour gérer les shaders OpenGL (vertex/fragment)
class Shader:
    def create_shader(shader_type, source):
        # Compile un shader OpenGL à partir du code source fourni
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        # Vérifie la compilation et affiche une erreur si besoin 
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            error = GL.glGetShaderInfoLog(shader).decode()
            print(f"Shader compilation error: {error}")
            GL.glDeleteShader(shader)
            return None
        return shader

    
    def create_program_from_file(vertex_file_path, fragment_file_path):
        # Crée un programme OpenGL à partir de deux fichiers shader (vertex et fragment)
        try:
            # Lecture des fichiers shader 
            with open(vertex_file_path, 'r') as f:
                vertex_source = f.read()
            with open(fragment_file_path, 'r') as f:
                fragment_source = f.read()
            # Compilation des shaders
            vertex_shader = Shader.create_shader(GL.GL_VERTEX_SHADER, vertex_source)
            fragment_shader = Shader.create_shader(GL.GL_FRAGMENT_SHADER, fragment_source)
            if not vertex_shader or not fragment_shader:
                return None
            # Création et liaison du programme OpenGL
            program = GL.glCreateProgram()
            GL.glAttachShader(program, vertex_shader)
            GL.glAttachShader(program, fragment_shader)
            GL.glLinkProgram(program)
            if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
                error = GL.glGetProgramInfoLog(program).decode()
                print(f"Program linking error: {error}")
                GL.glDeleteProgram(program)
                return None
            # Nettoyage des shaders 
            GL.glDeleteShader(vertex_shader)
            GL.glDeleteShader(fragment_shader)
            return program
        except Exception as e:
            print(f"Error creating shader program: {e}")
            return None