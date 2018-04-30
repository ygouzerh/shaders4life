#--------------------- Simple Shader
COLOR_VERT_POS = """#version 330 core
layout(location = 0) in vec3 position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
out vec3 fragColor;

void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    fragColor = position;
}"""


COLOR_FRAG_POS = """#version 330 core
in vec3 fragColor;
out vec4 outColor;
void main() {
    outColor = vec4(fragColor, 1);
}"""
