#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 Color;
in vec2 TexCoord;

out vec4 FragColor;

void main() {
    // Sol : motif régulier (lignes fines)
    if (abs(Normal.x) < 0.001 && abs(Normal.y - 1.0) < 0.001 && abs(Normal.z) < 0.001 && abs(FragPos.y) < 0.01) {
        float lineWidth = 0.05;
        float gridSize = 1.0;
        float fx = abs(fract(FragPos.x / gridSize) - 0.5);
        float fz = abs(fract(FragPos.z / gridSize) - 0.5);
        float line = step(lineWidth, fx) * step(lineWidth, fz);
        vec3 gridColor = mix(vec3(0.2, 0.2, 0.2), vec3(0.6, 0.6, 0.6), line);
        FragColor = vec4(gridColor, 1.0);
    } else {
        FragColor = vec4(Color, 1.0);
    }
}