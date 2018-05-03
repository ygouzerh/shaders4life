import numpy as np
import OpenGL.GL as GL
from VertexArray import VertexArray
from scipy import misc
from Shader import Shader
from terrain import computeNormalTriangle
from random import random
from math import sqrt
import copy


BASE_SIZE = 2
MAX_DEPTH = 2

def essaiTriangleTriforce() :
        coin1 = (0, 0, 0)
        coin2 = (0.87*BASE_SIZE, 0, 1*BASE_SIZE)
        coin3 = (0, 0, 1*BASE_SIZE)
        triangles = triforceTreatment(coin1, coin2, coin3)
        return triangles

def longueurArrete(point1, point2) :
    return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2)

def triforceTreatment(coin1, coin2, coin3, height_spike=0.3) :
    normale = computeNormalTriangle(coin1, coin2, coin3)
    # Phase de séparation :
    # Première séparation :
    triangles1 = separationTriangle(coin1, coin2, coin3)
    triangles2 = []
    normales = []
    modification4, modification5, modification6 = (random()-0.5)*height_spike, (random()-0.5)*height_spike, (random()-0.5)*height_spike
    for i in range(len(triangles1)//3):
        coin1 = triangles1[i*3]
        coin2 = triangles1[i*3+1]
        coin3 = triangles1[i*3+2]
        triangle = separationTriangle(coin1, coin2, coin3)
        # On change les coordonnées des points intérieurs
        if i==0:
            # Triangle 1
            nouveau_point5 = (triangle[5][0] + modification5*normale[0], triangle[5][1] + modification5*normale[1], triangle[5][2] + modification5*normale[2] )
            triangle[5] = nouveau_point5
            triangle[7] = nouveau_point5
            triangle[10] = nouveau_point5

        elif i==1:
            # Triangle 2
            nouveau_point6 = (triangle[2][0] + modification6*normale[0], triangle[2][1] + modification6*normale[1], triangle[2][2] + modification6*normale[2] )
            triangle[2] = nouveau_point6
            triangle[6] = nouveau_point6
            triangle[11] = nouveau_point6
        elif i==2:
            # Triangle 3
            nouveau_point4 = (triangle[1][0] + modification4*normale[0], triangle[1][1] + modification4*normale[1], triangle[1][2] + modification4*normale[2] )
            triangle[1] = nouveau_point4
            triangle[3] = nouveau_point4
            triangle[9] = nouveau_point4
        else :
            # Triangle 4
            triangle[1] = nouveau_point6
            triangle[3] = nouveau_point6
            triangle[9] = nouveau_point6
            triangle[5] = nouveau_point4
            triangle[7] = nouveau_point4
            triangle[10] = nouveau_point4
            triangle[2] = nouveau_point5
            triangle[6] = nouveau_point5
            triangle[11] = nouveau_point5

        #Normales :
        for j in range(len(triangle)//3):
            point1 = triangle[j*3]
            point2 = triangle[j*3+1]
            point3 = triangle[j*3+2]
            normale_courante = computeNormalTriangle(point1, point2, point3)
            normales.append(normale_courante)
            normales.append(normale_courante)
            normales.append(normale_courante)

        triangles2.extend(triangle)
    return triangles2, normales

def separationTriangle(point1, point2, point3) :
    point4 = milieuArrete(point1, point2)
    point5 = milieuArrete(point2, point3)
    point6 = milieuArrete(point3, point1)
    return [point1, point4, point6, point4, point2, point5, point6, point5, point3, point4, point5, point6]



def milieuArrete(point1, point2) :
    return ((point1[0]+point2[0])/2, (point1[1]+point2[1])/2,  (point1[2]+point2[2])/2)

TRI_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normales;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 lightDirection;


out float coefLight;

void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    coefLight = max(dot(transpose(inverse(mat3(model)))*normales,lightDirection)*1.5, 0)*0.0001;
}"""


TRI_FRAG = """#version 330 core
out vec4 outColor;
in float coefLight;

void main() {
    outColor = vec4(0.3*coefLight, 0.7*coefLight, 0.3*coefLight, 1);
}"""


class TriangleTriforce:
    def __init__(self, lightDirection):
        rocher_array, normales = essaiTriangleTriforce()
        self.vertex_array = VertexArray(attributes = [rocher_array, normales])
        self.shader = Shader(TRI_VERT, TRI_FRAG)
        self.lightDirection = lightDirection


    def draw(self, projection, view, model, **param):
        names = ['view', 'projection', 'model', 'lightDirection']

        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}
        GL.glUseProgram(self.shader.glid)

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)
        GL.glUniform3fv(loc['lightDirection'], 1, self.lightDirection)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertex_array.draw(GL.GL_TRIANGLES)
