import sys
sys.path.append('./Objects')
sys.path.append('./Utils')
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat)
from Node import Node
from Shader import Shader
from loader import load
from Textures import load_textured, TexturedPlane
from random import randrange, randint, choice
import OpenGL.GL as GL

"""
Map to define all the nodes used in the world
"""
class Map:
    """ Return the top nodes of the world map"""

    def __init__(self, map_width, map_height, map_depth):
        """ Get the width, the height and the depth of the map """
        self.map_width = map_width
        self.map_height = map_height
        self.map_depth = map_depth

    def generate_nodes(self, mesh, number, rotation_max=360, axis_rotation=(0, 1, 0), axis_translation=(1, 0, 1)):
        """
            Generate all leaf nodes
            rotation_max = rotation max possible on the axes
            axis_rotation = axe of rotation, ex (0, 1, 0) = only on y
            axis_translation = axe of translation, ex (1, 0, 1) = for humans
        """
        nodes = []
        for i in range(number):
            node = Node('')
            node.add(mesh)
            self.randomize_creation(node, rotation_max, axis_rotation, axis_translation)
            nodes.append(node)
        return nodes

    def randomize_creation(self, node, rotation_max, axis_rotation, axis_translation):
        """
            Modify randomly a nodes
            Using the parameters of the map
        """
        node.translate()
        node.rotate(axis_rotation, randint(-rotation_max, rotation_max))
        node.translate(axis_translation[0]*randint(-self.map_width, self.map_width), \
                        axis_translation[1]*randint(-self.map_height, self.map_height), \
                        axis_translation[2]*randint(-self.map_depth, self.map_depth))

    def trex(self):
        """ Generate the trex """
        mesh_trex = load_textured("Objects/trex/trex.obj")[0]
        nodes_trex = Node("all_trex", children=self.generate_nodes(mesh_trex, 10))
        return nodes_trex

    def simple_ground(self):
        """ Load a simple ground """
        ground_mesh = TexturedPlane("Objects/ground/moss.jpg")
        ground_node = Node("ground", children=[ground_mesh])
        ground_node.rotate((1, 0, 0), -90)
        ground_node.scale_total(10)
        return ground_node

    def skybox(self):
        """ Create the skybox """
        mesh_skybox = load_textured("Objects/skybox/skybox.obj")[0]
        node_skybox = Node("skybox", children=[mesh_skybox])
        node_skybox.rotate((1, 0, 0), -90)
        node_skybox.scale_total(10)
        return node_skybox

    def create(self):
        top_node = Node('top')
        mesh_trex = load_textured("Objects/trex/trex.obj")[0]
        trex_one = Node("trex_one", children=[mesh_trex])
        top_node.add(self.skybox(), self.simple_ground(), self.trex(), trex_one)
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
