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


MAX_DEPTH = 2

def recursiveRock(profondeur, rocher, coin1, coin2, coin3):
    rocher.append(coin1)
    rocher.append(coin2)
    rocher.append(coin3)
    if profondeur == MAX_DEPTH:
        return
    else  :
        hauteur = 1/(profondeur**3+1)
        centre = centreTriangle(coin1, coin2, coin3)
        normale = computeNormalTriangle(coin1, coin2, coin3)
        # Nouveau coin
        coin4 = (centre[0] + normale[0]*hauteur, centre[1] + normale[1]*hauteur, centre[2] + normale[2]*hauteur)
        recursiveRock(profondeur+1, rocher, coin1, coin3, coin4)
        recursiveRock(profondeur+1, rocher, coin2, coin1, coin4)
        recursiveRock(profondeur+1, rocher, coin3, coin2, coin4)

def createRandomRockRecursive(taille_initiale_rayon=2) :
    rocher = []
    normales = []
    # On crée une pyramide initialement.
    coin1 = (0, 0, 0)
    coin2 = ((1 + random()*0.5)*taille_initiale_rayon, 0, (1 + random()*0.5)**taille_initiale_rayon)
    coin3 = (0, 0, (1 + random()*0.5)**taille_initiale_rayon)

    recursiveRock(0, rocher, coin1, coin2, coin3)

    return rocher, normales



def createRandomRockIterative(complexite, seuilChangement = 0, taille_initiale_rayon=2, intensite_reduction_longueur = 5, height_spike = 0.3, borne_intensite=0.5) :
    rocher = []
    # normales = []
    # On crée un tetraèdre initialement.
    coin1 = (0, 0, 0)
    coin2 = (taille_initiale_rayon, 0, taille_initiale_rayon)
    coin3 = (0, 0, taille_initiale_rayon)
    centre = centreTriangle(coin1, coin2, coin3)
    nombre_aleatoire = random()
    coin4 = (centre[0], taille_initiale_rayon + (nombre_aleatoire - 0.5)*taille_initiale_rayon, centre[2])
    centre_tetraedre_initial = (centre[0], centre[1] + (nombre_aleatoire-0.5)*taille_initiale_rayon/2, centre[2])

    rocher.append(coin1)
    rocher.append(coin2)
    rocher.append(coin3)
    # normale = computeNormalTriangle(coin1, coin3, coin2)
    # normales.append(normale)
    # normales.append(normale)
    # normales.append(normale)

    rocher.append(coin1)
    rocher.append(coin3)
    rocher.append(coin4)
    # normale = computeNormalTriangle(coin1, coin4, coin3)
    # normales.append(normale)
    # normales.append(normale)
    # normales.append(normale)

    rocher.append(coin2)
    rocher.append(coin1)
    rocher.append(coin4)
    # normale = computeNormalTriangle(coin2, coin4, coin1)
    # normales.append(normale)
    # normales.append(normale)
    # normales.append(normale)

    rocher.append(coin3)
    rocher.append(coin2)
    rocher.append(coin4)
    # normale = computeNormalTriangle(coin3, coin4, coin2)
    # normales.append(normale)
    # normales.append(normale)
    # normales.append(normale)


    for i in range(complexite) :
        longueur_actuelle = len(rocher)//3
        nouveau_rocher = []
        nouvelles_normales = []
        for j in range(longueur_actuelle):
            coin1 = rocher[j*3]
            coin2 = rocher[j*3 + 1]
            coin3 = rocher[j*3 + 2]
            if j>=0:
                # On complexifie la face :
                hauteur = -max(random(), borne_intensite)*taille_initiale_rayon/((i+intensite_reduction_longueur))
                centre = centreTriangle(coin1, coin2, coin3)
                normale = computeNormalTriangle(coin1, coin3, coin2)

                # Nouveau coin

                coin4 = (centre[0] + normale[0]*hauteur, centre[1] + normale[1]*hauteur, centre[2] + normale[2]*hauteur)
                # On crée les nouvelles faces :
                nouveau_rocher.append(coin1)
                nouveau_rocher.append(coin4)
                nouveau_rocher.append(coin3)
                # normale = computeNormalTriangle(coin1, coin4, coin3)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)

                nouveau_rocher.append(coin2)
                nouveau_rocher.append(coin4)
                nouveau_rocher.append(coin1)
                # normale = computeNormalTriangle(coin2, coin4, coin1)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)


                nouveau_rocher.append(coin3)
                nouveau_rocher.append(coin4)
                nouveau_rocher.append(coin2)
                # normale = computeNormalTriangle(coin3, coin4, coin2)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)
                # nouvelles_normales.append(normale)

            else :
                # On ne change rien. On ajoute ça au début de la liste pour qu'ils soient sélectionner prioritairement la prochaine fois.
                nouveau_rocher.append(coin1)
                nouveau_rocher.append(coin2)
                nouveau_rocher.append(coin3)
                # nouvelles_normales.append(normales[j*3])
                # nouvelles_normales.append(normales[j*3])
                # nouvelles_normales.append(normales[j*3])
        rocher = copy.copy(nouveau_rocher)
        # normales = copy.copy(nouvelles_normales)

    rocher_final = []
    normales_finales = []

    for i in range(len(rocher)//3):
        point1 = rocher[i*3]
        point2 = rocher[i*3 +1]
        point3 = rocher[i*3 +2]
        nouveaux_triangles, nouvelles_normales = triforceTreatment(point1, point2, point3, height_spike)
        rocher_final.extend(nouveaux_triangles)
        normales_finales.extend(nouvelles_normales)

    return rocher_final, normales_finales, centre_tetraedre_initial

def centreTriangle(point1, point2, point3) :
    return ((point1[0] + point2[0] + point3[0])/3, (point1[1] + point2[1] + point3[1])/3, (point1[2] + point2[2] + point3[2])/3 )


ROCHER_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normales;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightDirection;
uniform vec3 color;

out vec3 frag_position;
out float coefLight;
out vec3 color_coef;
void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    coefLight = max(dot(transpose(inverse(mat3(model)))*normales,lightDirection)*1.5, 0)*0.0001;
    color_coef = color;
}"""


ROCHER_FRAG = """#version 330 core
out vec4 outColor;
in vec3 frag_position;
in float coefLight;
in vec3 color_coef;

void main() {
    outColor = vec4(color_coef[0]/4 + color_coef[0]*coefLight, color_coef[1]/4 + color_coef[1]*coefLight, color_coef[2]/4 + color_coef[2]*coefLight, 1);
}"""


class Rocher(Node):
    def __init__(self, lightDirection, complexite_rocher = 6, seuilChangement = 0, taille_initiale_rayon=2, intensite_reduction_longueur = 3, height_spike = 0.5, color=[0.4,0.4,0.4], borne_intensite=0.2):
        super().__init__()
        rocher_array, normales, centre = createRandomRockIterative(complexite_rocher, seuilChangement, taille_initiale_rayon, intensite_reduction_longueur, borne_intensite)
        self.vertex_array = VertexArray(attributes = [rocher_array, normales])
        self.shader = Shader(ROCHER_VERT, ROCHER_FRAG)
        self.lightDirection = lightDirection
        self.centre = centre
        self.color = color
        # self.add(Axis())


    def draw(self, projection, view, model, **param):
        names = ['view', 'projection', 'model', 'lightDirection', 'color']

        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}
        GL.glUseProgram(self.shader.glid)

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)
        GL.glUniform3fv(loc['lightDirection'], 1, self.lightDirection)
        GL.glUniform3fv(loc['color'], 1, self.color)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertex_array.draw(GL.GL_TRIANGLES)
        super().draw(projection, view, model, **param)
