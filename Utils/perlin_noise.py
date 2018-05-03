#!/usr/bin/env python3
from math import cos, pi

#Retrourne une valeur pseudo aléatoire entre 0 et 1
def noise(var):
    var = (var<<13)^var
    return (((var * (var * var * 15731 + 789221) + 1376312589) & 0xfffffff) / 2147483648.0)

#Retourne un vecteur représentant une matrice 3D avec tous les bruits
def noise2D(x,y):
    return noise(int(noise(x) * 90000+y))#Multiplication pour aggrandir les ecarts

#Interpolation par cosinus pour obtenir des courbes arrondies
#TODO:Remplacer  cosin interp par cubic interp
def interpolate(a, b, time):
    return (1. - time) * a + time * b;

def smoothNoise(x):

    if x >= 0:
        intX = int(x)
    else:
        intX = int(x) - 1
    fracX = x-intX
    return  interpolate(noise(intX),noise(intX+1),fracX)

def smoothNoise2D(x,y):

    if x >= 0:
        intX = int(x);
    else:
        intX = int(x) - 1;
    if y >= 0:
        intY = int(y);
    else:
        intY = int(y) - 1;
    fracX = x-intX
    fracY = y-intY

    A = noise2D(intX,intY)
    B = noise2D(intX+1,intY)
    C = noise2D(intX,intY+1)


    interX = interpolate(A,B,fracX)
    interY = interpolate(A,C,fracX)

    return interpolate(interX,interY, fracY)

#nOctaves : nombre d'appel a smoothNoise
#freq: "Force" du premier appel
#Persist: modif freq a chaque appel
def perlinNoise2D(nOctaves, freq, persist, x, y):
    amplitude = 1
    curFreq = freq
    var = 0

    for i in range(nOctaves):
        var += smoothNoise2D(int(x * curFreq) + i * 4096, int(y * curFreq)+ i * 4096) # Addition pour translater le centre du motif
        amplitude = amplitude * persist
        curFreq = curFreq*2

    return var * (1 - persist)/(1-amplitude)

def perlinText(height, width):
    tex = []
    for i in range(height):
        row = []
        for j in range(width):
            color = perlinNoise2D(10,1000,0.47,i,j)*255
            row.append([color, color+20, color])
        tex.append(row)
    return tex

#print(perlinText(10,10))
