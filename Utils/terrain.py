import numpy as np
import OpenGL.GL as GL
from VertexArray import VertexArray
from scipy import misc
from Shader import Shader
from Node import Node, Axis

Height_Ground = 50

def trianglesFromImages(matrix_image, longueur_arrete = Height_Ground/10) :
    """Retourne un tableau de la taille de la matrice contenant à chaque case les
    deux triangles composant un carré ainsi que leur normales"""
    taille_i = matrix_image.shape[0]
    taille_j = matrix_image.shape[1]
    triangles = []
    # On cherche le min et le max de la matrice :
    max_height = matrix_image.max()
    min_height = matrix_image.min()

    for i in range(taille_i - 2):
        for j in range(taille_j - 2):
            coin_bas_droit = [(i+1)*longueur_arrete, (matrix_image[i+1][j+1][0] - min_height)/max_height*Height_Ground, (j+1)*longueur_arrete] # À chaque fois, on prendra la première coordonnée, car ce sont des niveaux de gris.
            coin_bas_gauche = [(i+1)*longueur_arrete, (matrix_image[i+1][j][0] - min_height)/max_height*Height_Ground, j*longueur_arrete]
            coin_haut_droit = [i*longueur_arrete, (matrix_image[i][j+1][0] - min_height)/max_height*Height_Ground, (j+1)*longueur_arrete]
            coin_haut_gauche = [i*longueur_arrete, (matrix_image[i][j][0] - min_height)/max_height*Height_Ground, j*longueur_arrete]

            carre = []
            # Premier triangle d'un carré :
            normale = computeNormalTriangle(coin_haut_gauche, coin_bas_gauche, coin_bas_droit)
            carre.append(([coin_haut_gauche, coin_bas_droit, coin_bas_gauche], normale))

            # Second triangle :
            normale = computeNormalTriangle(coin_haut_gauche, coin_bas_droit, coin_haut_droit)
            carre.append(([coin_haut_gauche, coin_haut_droit, coin_bas_droit], normale))
            triangles.append(carre)

    return triangles

def computeNormalVertices(triangles, taille_i, taille_j):
    """Retourne un tableau de la même taille que l'entrée avec à chaque case
    les normales de chaques vertices"""
    normales = []
    for i in range(taille_i):
        for j in range(taille_j) :
            if j == 0 :
                # On est sur le bord gauche :
                if i == 0:
                    normale_coin_haut_gauche = getNormalCoinCoin(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBordure(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBasic(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBordure(4, triangles, taille_i, taille_j, i, j)

                elif i == taille_i-1:
                    normale_coin_haut_gauche = getNormalCoinCoin(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBasic(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBasic(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinCoin(4, triangles, taille_i, taille_j, i, j)
                else :
                    normale_coin_haut_gauche = getNormalCoinCoin(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBasic(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBasic(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBordure(4, triangles, taille_i, taille_j, i, j)

            elif j == taille_j - 1 :
                # On est sur le bord droit
                if i == 0:
                    normale_coin_haut_gauche = getNormalCoinBordure(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinCoin(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBordure(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBasic(4, triangles, taille_i, taille_j, i, j)

                elif i == taille_i-1:
                    normale_coin_haut_gauche = getNormalCoinBasic(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBordure(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinCoin(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBasic(4, triangles, taille_i, taille_j, i, j)
                else :
                    normale_coin_haut_gauche = getNormalCoinBasic(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBordure(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBordure(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBasic(4, triangles, taille_i, taille_j, i, j)

            if i == 0 :
                # On est sur le bord haut
                if j == 0:
                    # Déjà fait
                    pass
                elif j == taille_j-1:
                    # Déjà fait
                    pass
                else :
                    normale_coin_haut_gauche = getNormalCoinBordure(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBordure(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBasic(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBasic(4, triangles, taille_i, taille_j, i, j)

            elif i == taille_i - 1 :
                # On est sur le bord bas
                if j == 0:
                    # Déjà fait
                    pass
                elif j == taille_j-1:
                    # Déjà fait
                    pass
                else :
                    normale_coin_haut_gauche = getNormalCoinBasic(1, triangles, taille_i, taille_j, i, j)
                    normale_coin_haut_droit = getNormalCoinBasic(2, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_droit = getNormalCoinBordure(3, triangles, taille_i, taille_j, i, j)
                    normale_coin_bas_gauche = getNormalCoinBordure(4, triangles, taille_i, taille_j, i, j)

            elif  j <= taille_j - 2 and j >= 1:
                # On est au centre. Dans ce cas on récupère :
                # Triangle bas
                # Coin haut gauche
                normale_coin_haut_gauche = getNormalCoinBasic(1, triangles, taille_i, taille_j, i, j)
                # Coin coin bas droit
                normale_coin_bas_droit = getNormalCoinBasic(3, triangles, taille_i, taille_j, i, j)
                # Coin bas gauche
                normale_coin_bas_gauche = getNormalCoinBasic(4, triangles, taille_i, taille_j, i, j)
                # Triangle haut
                # Coin haut droit
                normale_coin_haut_droit = getNormalCoinBasic(2, triangles, taille_i, taille_j, i, j)

            normales.append(normale_coin_haut_gauche, normale_coin_bas_droit, normale_coin_bas_gauche, normale_coin_haut_gauche, normale_coin_haut_droit, normale_coin_bas_droit)

def getNormalCoinBasic(numeroCoin, trianglesAndNormals, taille_i, taillej,i, j):
    """Retourne la normale quand tout va bien"""
    if numeroCoin == 1:
        return np.mean(trianglesAndNormals[j-1 + (i-1)*taille_j][0][1],
                                            trianglesAndNormals[j-1 + (i-1)*taille_j][1][1],
                                            trianglesAndNormals[j + i*taille_j][0][1],
                                            trianglesAndNormals[j + i*taille_j][1][1],
                                            trianglesAndNormals[j + (i-1)*taille_j][0][1],
                                            trianglesAndNormals[j-1 + (i)*taille_j][1][1])
    elif numeroCoin == 2 :
        return np.mean(trianglesAndNormals[j + (i-1)*taille_j][0][1],
                                         trianglesAndNormals[j + (i-1)*taille_j][1][1],
                                         trianglesAndNormals[j + (i)*taille_j][1][1],
                                         trianglesAndNormals[j+1 + (i-1)*taille_j][0][1],
                                         trianglesAndNormals[j+1 + (i)*taille_j][1][1],
                                         trianglesAndNormals[j+1 + (i)*taille_j][0][1])

    elif numeroCoin == 3 :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][0][1],
                                         trianglesAndNormals[j + (i)*taille_j][1][1],
                                         trianglesAndNormals[j+1 + (i)*taille_j][0][1],
                                         trianglesAndNormals[j + (i+1)*taille_j][1][1],
                                         trianglesAndNormals[j+1 + (i+1)*taille_j][1][1],
                                         trianglesAndNormals[j+1 + (i+1)*taille_j][0][1])

    else :
        return np.mean(trianglesAndNormals[j-1 + (i)*taille_j][0][1],
                                         trianglesAndNormals[j-1 + (i)*taille_j][1][1],
                                         trianglesAndNormals[j + (i)*taille_j][0][1],
                                         trianglesAndNormals[j-1 + (i+1)*taille_j][1][1],
                                         trianglesAndNormals[j + (i+1)*taille_j][1][1],
                                         trianglesAndNormals[j + (i+1)*taille_j][0][1])

def getNormalCoinCoin(numeroCoin, trianglesAndNormals, taille_i, taille_j,i, j):
    """Retourne la normale quand tout va bien"""
    if numeroCoin == 1:
        indice = j + i*taille_j
        return (trianglesAndNormals[indice][0][1] +  trianglesAndNormals[indice][1][1])/2
    elif numeroCoin == 2 :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][1][1])

    elif numeroCoin == 3 :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][0][1],
                                         trianglesAndNormals[j + (i)*taille_j][1][1])

    else :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][0][1])

def getNormalCoinBordure(numeroCoin, trianglesAndNormals, taille_i, taillej,i, j):
    """Retourne la normale quand tout va bien"""
    if numeroCoin == 1:
        return np.mean(trianglesAndNormals[j + i*taille_j][0][1],
                                            trianglesAndNormals[j + i*taille_j][1][1],
                                            trianglesAndNormals[j + (i-1)*taille_j][0][1])
    elif numeroCoin == 2 :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][1][1],
                        trianglesAndNormals[j+1 + (i)*taille_j][1][1],
                        trianglesAndNormals[j+1 + (i)*taille_j][0][1])

    elif numeroCoin == 3 :
        return np.mean(trianglesAndNormals[j + (i)*taille_j][0][1],
                                         trianglesAndNormals[j + (i)*taille_j][1][1],
                                         trianglesAndNormals[j + (i+1)*taille_j][1][1])

    else :
        return np.mean(trianglesAndNormals[j-1 + (i)*taille_j][0][1],
                                         trianglesAndNormals[j-1 + (i)*taille_j][1][1],
                                         trianglesAndNormals[j + (i)*taille_j][0][1])

def computeNormalTriangle(coin1, coin2, coin3) :
    X = (coin2[1]-coin1[1])*(coin3[2]-coin1[2]) - (coin2[2]-coin1[2])*(coin3[1]-coin1[1])
    Y = (coin2[2]-coin1[2])*(coin3[0]-coin1[0]) - (coin2[0]-coin1[0])*(coin3[2]-coin1[2])
    Z = (coin2[0]-coin1[0])*(coin3[1]-coin1[1]) - (coin2[1]-coin1[1])*(coin3[0]-coin1[0])
    return (X, Y, Z)

def generateTerrainPlat(taille, longueur_arrete = 5):
    """ On crée un np.array avec les vertex pour le terrain """
    terrain_vertex = []
    normales = []
    for i in range(taille):
        for j in range(taille):
            coin_bas_droit = ((i+1)*longueur_arrete, (j+1)*longueur_arrete)
            coin_bas_gauche = ((i+1)*longueur_arrete, j*longueur_arrete)
            coin_haut_droit = (i*longueur_arrete, (j+1)*longueur_arrete)
            coin_haut_gauche = (i*longueur_arrete, j*longueur_arrete)
            # Premier triangle d'un carré :
            terrain_vertex.append(coin_haut_gauche)
            terrain_vertex.append(coin_bas_gauche)
            terrain_vertex.append(coin_bas_droit)

            # Second triangle :
            terrain_vertex.append(coin_haut_gauche)
            terrain_vertex.append(coin_bas_droit)
            terrain_vertex.append(coin_haut_droit)
            normale = computeNormalTriangle(coin_haut_gauche, coin_bas_droit, coin_haut_droit)
            normales.append(normale, normale, normale)

    return np.array(terrain_vertex, np.float32), normales

def generateTerrainFromImage(matrix_image, longueur_arrete = Height_Ground/100) :
    taille_i = matrix_image.shape[0]
    taille_j = matrix_image.shape[1]
    terrain_vertex = []
    normales = []
    # On cherche le min et le max de la matrice :
    max_height = matrix_image.max()
    min_height = matrix_image.min()

    for i in range(taille_i - 2):
        for j in range(taille_j - 2):
            coin_bas_droit = ((i+1)*longueur_arrete, (matrix_image[i+1][j+1][0] - min_height)/max_height*Height_Ground, (j+1)*longueur_arrete) # À chaque fois, on prendra la première coordonnée, car ce sont des niveaux de gris.
            coin_bas_gauche = ((i+1)*longueur_arrete, (matrix_image[i+1][j][0] - min_height)/max_height*Height_Ground, j*longueur_arrete)
            coin_haut_droit = (i*longueur_arrete, (matrix_image[i][j+1][0] - min_height)/max_height*Height_Ground, (j+1)*longueur_arrete)
            coin_haut_gauche = (i*longueur_arrete, (matrix_image[i][j][0] - min_height)/max_height*Height_Ground, j*longueur_arrete)
            # Premier triangle d'un carré :
            terrain_vertex.append(coin_haut_gauche)
            terrain_vertex.append(coin_bas_droit)
            terrain_vertex.append(coin_bas_gauche)
            normale = computeNormalTriangle(coin_haut_gauche, coin_bas_gauche, coin_bas_droit)
            # Second triangle :
            terrain_vertex.append(coin_haut_gauche)
            terrain_vertex.append(coin_haut_droit)
            terrain_vertex.append(coin_bas_droit)
            normale2 = computeNormalTriangle(coin_haut_gauche, coin_bas_droit, coin_haut_droit)
            normales.append(normale)
            # normales.append(normale)
            # normales.append(normale)
            normales.append(normale2)
            # normales.append(normale2)
            # normales.append(normale2)


    # return np.array(terrain_vertex, np.float32)
    return terrain_vertex, normales

TERRAIN_VERT = """#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normales;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 light_direction;
uniform float lightIntensity;

out float height;
out float coefLight;
void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    height = position.y;
    coefLight = max(dot(transpose(inverse(mat3(model)))*normales,light_direction)*1.5, 0)*0.000001;
}"""


TERRAIN_FRAG = """#version 330 core
in float height;
in float coefLight;
out vec4 outColor;
const int AMPLITUDE = %d;
void main() {

    outColor = vec4((0.40 - 0.20*height/AMPLITUDE), (0.35 + 0.10*height/AMPLITUDE), (0.10 + 0.05*height/AMPLITUDE), 0)*0.5;
    outColor += vec4((0.50 - 0.10*height/AMPLITUDE)*coefLight, (0.35 + 0.10*height/AMPLITUDE)*coefLight, (0.30 + 0.10*height/AMPLITUDE)*coefLight , 1);
}"""%Height_Ground


class Terrain(Node):
    def __init__(self, nom_image, light_direction,  longueur_arrete = 2):
        super().__init__()
        matrice_image = misc.imread(nom_image)
        terrain_array, normales = generateTerrainFromImage(matrice_image, longueur_arrete)
        self.vertex_array = VertexArray(attributes = [terrain_array, normales])
        self.shader = Shader(TERRAIN_VERT, TERRAIN_FRAG)
        self.light_direction = light_direction
        self.add(Axis())

    def draw(self, projection, view, model, **param):

        names = ['view', 'projection', 'model', 'light_direction']


        loc = {n: GL.glGetUniformLocation(self.shader.glid, n) for n in names}
        GL.glUseProgram(self.shader.glid)


        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)
        GL.glUniform3fv(loc['light_direction'], 1, self.light_direction)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertex_array.draw(GL.GL_TRIANGLES)
        super().draw(projection, view, model, **param)
