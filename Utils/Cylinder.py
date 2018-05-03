import sys
import numpy as np
sys.path.append("../Utils")
from loader import ColorMesh
from math import sin, cos, pi


import itertools as it

def pairIter(iterable):
    a, b = it.tee(iterable)
    next(b)
    return zip(a, b)

class Cylinder(ColorMesh):
    def __init__(self, nbFaces = 9 , height = 2):
        triangles = []

        points_cercle = [(cos(piVal), height/2, sin(piVal)) for piVal in np.arange(0,2*pi, 2*pi/nbFaces)]
        points_cercle2 = [(cos(piVal), -height/2, sin(piVal)) for piVal in np.arange(0,2*pi, 2*pi/nbFaces)]
        for p, p2 in pairIter(points_cercle):
            triangles += [ (0,0,height/2), p, p2]
        triangles += ((0,0,height/2), points_cercle[-1], points_cercle[0])
        for p, p2 in pairIter(points_cercle2):
            triangles += [p, (0,0,-height/2), p2]
        triangles += (points_cercle2[-1], (0,0,-height/2), points_cercle2[0])

        for topCircle, botCircle, in zip(pairIter(points_cercle), pairIter(points_cercle2)):
            triangles += [topCircle[0], botCircle[1], topCircle[1]]
            triangles += [topCircle[0], botCircle[0], botCircle[1]]
        triangles += [points_cercle2[-1], points_cercle[0], points_cercle[-1]]
        triangles += [points_cercle2[0], points_cercle[0], points_cercle2[-1]]


        self.position = np.array(triangles,np.float32)
        super().__init__([self.position])
