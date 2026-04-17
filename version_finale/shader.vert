#version 330 core

// Attributs d'entrée (un par sommet)
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;
layout(location = 3) in vec2 texCoord;

// Matrices de transformation
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

// Sorties vers le fragment shader
out vec3 FragPos;
out vec3 Normal;
out vec3 Color;
out vec2 TexCoord;

void main() {
    // Calcul de la position du sommet dans l'espace monde
    FragPos = vec3(model * vec4(position, 1.0));
    
    // Calcul de la normale transformée
    Normal = mat3(transpose(inverse(model))) * normal;
    
    // Passage de la couleur et des coordonnées de texture
    Color = color;
    TexCoord = texCoord;
    
    // Position finale du sommet
    gl_Position = projection * view * model * vec4(position, 1.0);
}