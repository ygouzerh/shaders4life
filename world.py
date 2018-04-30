import sys
sys.path.append('./Objects')
sys.path.append('./Utils')
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat)
from Node import Node
from Shader import Shader
from loader import load

"""
Map to define all the nodes used in the world
"""
class Map:
    """ Return the top nodes of the world map"""
    @staticmethod
    def create():
        top_node = Node('top')
        cube_mesh = load("Objects/cube/cube.obj")[0]
        cube_node = Node("cube1");
        cube_node.add(cube_mesh)
        top_node.add(cube_node)
        return top_node

class MapCube:
    """ Map for only one cube"""
    @staticmethod
    def create():
        top_node = Node('top')
        cube_mesh = load("Objects/cube/cube.obj")[0]
        cube_node = Node("cube1");
        cube_node.add(cube_mesh)
        top_node.add(cube_node)
        return top_node
