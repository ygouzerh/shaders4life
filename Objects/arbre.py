import numpy as np
import OpenGL.GL as GL
from VertexArray import VertexArray
from scipy import misc
from Shader import Shader
from Node import Node, Axis
from terrain import computeNormalTriangle
from random import random
from math import sqrt
from triforce import triforceTreatment
import copy
from rocher import Rocher
from loader import load
from transform import translate, scale

def createTronc(arrivee) :
    cylindre = load("Objects/cylinder.obj")


ARBRE_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normales;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightDirection;

out vec3 frag_position;
out float coefLight;
void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    coefLight = max(dot(transpose(inverse(mat3(model)))*normales,lightDirection)*1.5, 0)*0.0001;
}"""


ARBRE_FRAG = """#version 330 core
out vec4 outColor;
in vec3 frag_position;
in float coefLight;

void main() {
    outColor = vec4(0.2 + 0.3*coefLight, 0.2 + 0.7*coefLight, 0.2 + 0.3*coefLight, 1);
}"""


TRONC_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normals;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightDirection;

out float coefLight;
void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    coefLight = max(dot(transpose(inverse(mat3(model)))*normals,lightDirection)*1.5, 0)*0.000001;
}"""


TRONC_FRAG = """#version 330 core
out vec4 outColor;
in float coefLight;

void main() {
    outColor = vec4(0.3/5 + 0.3*coefLight,0.15/5 + 0.15*coefLight, 0, 1);
}"""

class Arbre(Node):
    def __init__(self, lightDirection):
        super().__init__()
        # Tronc
        cylindre = load("Objects/cylinder.obj")[0]
        cylindre.shader = Shader(TRONC_VERT, TRONC_FRAG)
        # self.add(cylindre)
        # self.add(Rocher(lightDirection))
        self.cylindre = cylindre

        feuilles = Rocher(lightDirection, complexite_rocher = 3, intensite_reduction_longueur = 4, taille_initiale_rayon=2, color=[0.3,0.7,0.3], borne_intensite=0.4)
        noeud = Node(children = [feuilles], transform = translate(feuilles.centre[0]-1.5, feuilles.centre[1] + 1.5, feuilles.centre[2]-3))
        noeud2 = Node(children = [cylindre], transform = scale(0.2, 2, 0.2))
        self.add(noeud)
        self.add(noeud2)
        self.shader = Shader(ARBRE_VERT, ARBRE_FRAG)
        self.lightDirection = lightDirection
        # self.add(Axis())


    def draw(self, projection, view, model, **param):
        names = ['lightDirection']

        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}
        GL.glUseProgram(self.shader.glid)

        GL.glUniform3fv(loc['lightDirection'], 1, self.lightDirection)


        loc = {n: GL.glGetUniformLocation(self.cylindre.shader.glid, n) for n in names}
        GL.glUseProgram(self.cylindre.shader.glid)

        GL.glUniform3fv(loc['lightDirection'], 1, self.lightDirection)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        super().draw(projection, view, model, **param)
