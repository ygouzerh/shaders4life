from transform import identity, rotate
import glfw
from loader import ColorMesh
import numpy as np
import OpenGL.GL as GL
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat, quaternion_matrix,
                        quaternion_mul, quaternion_from_axis_angle)
from collections import defaultdict

class Node:
    """ Scene graph transform and parameter broadcast node """
    number_subnodes = 0
    def __init__(self, name='', transform=None, children=(), \
                translation_matrix=translate(), scale_matrix=scale(1), rotation_quaternion=quaternion(), axe=False,
                height_ground=0, \
                 **param):
        # Set all the arguments
        self.transform, self.param, self.name, \
        self.translation_matrix, self.scale_matrix, self.rotation_quaternion = \
        transform, param, name, translation_matrix, scale_matrix, rotation_quaternion
        self.children = defaultdict(list)
        self.height_ground = height_ground
        self.add(*children)
        if(axe):
            self.add(Axis())# Fait bugger le skinning

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        for child in drawables:
            if(isinstance(child, Node)):
                if(child.name == ''):
                    name = "NodeLocal"+str(Node.number_subnodes)
                else:
                    name = child.name
                NodeStorage.add_node(child)
            else:
                name = "ColorMeshLocal"+str(Node.number_subnodes)
                NodeStorage.add_colormesh(child)
            self.children[name].append(child)
            Node.number_subnodes += 1

    def set_height_ground(self, height_ground):
        """ Setter for height ground """
        self.height_ground = height_ground

    def draw(self, projection, view, model, **param):
        """ Recursive draw, passing down named parameters & model matrix. """
        # merge named parameters given at initialization with those given here
        param = dict(param, **self.param)
        if(self.transform is None):
            model =  model @ self.get_trs_matrix()
        else:
            model = model @ self.transform

        for childes in self.children.values():
            for child in childes:
                child.draw(projection, view, model, **param)

    def translate(self, x=0.0, y=0.0, z=0.0):
        """ Translate the node """
        self.translation_matrix = translate(x, y, z) @ self.translation_matrix
        print("Translate")

    def scale(self, x, y=None, z=None):
        """ Scale the node """
        self.scale_matrix = scale(x, y, z) @ self.scale_matrix

    def scale_total(self, value):
        """ Wrapper for min or max all the shape """
        self.scale(value, value, value)

    def rotate(self, axis=(1., 0., 0.), angle=0.0, radians=None):
        """ Rotate the node : warning, it's not using quaternion """
        # TODO : Verify the order of the multiplication
        self.rotation_quaternion = quaternion_mul(self.rotation_quaternion, quaternion_from_axis_angle(axis, angle, radians))

    def set_global_position(self, x=0.0, y=0.0, z=0.0):
        """ Reset global position """
        self.translation_matrix = translate(x, y , z)

    def set_global_rotation(self, axis=(1., 0., 0.), angle=0.0, radians=None):
        """ Reset global rotation """
        self.rotation_quaternion = quaternion_from_axis_angle(axis, angle, radians)

    def set_global_scale(self, x, y=None, z=None):
        """ Reset global scale """
        self.scale_matrix = scale(x, y, z)

    def get_trs_matrix(self):
        """ Get TRS matrix """
        return translate(0, self.height_ground, 0) @ self.translation_matrix @ quaternion_matrix(self.rotation_quaternion) @ self.scale_matrix

    def get_x(self):
        """ Return the x coordinates """
        return self.translation_matrix[0][3]

    def get_y(self):
        """ Return the y coordinates"""
        return self.translation_matrix[1][3]

    def get_z(self):
        """ Return the z coordinates"""
        return self.translation_matrix[2][3]

    def set_name(self, name):
        """ Setter for the name """
        self.name = name

class NodeStorage:
    """ HashMap to interact easily with all the nodes """
    nodes = dict()
    # TODO : Use defaultdict if needed
    @staticmethod
    def add_node(node):
        """ Add one node """
        if(node.name == ''):
            name = "ColorMesh"+str(len(NodeStorage.nodes))
        else:
            name = node.name
        NodeStorage.nodes.update({node.name : node})

    @staticmethod
    def add_colormesh(colormesh):
        """ Add one color mesh """
        NodeStorage.nodes.update({"ColorMesh"+str(len(NodeStorage.nodes)) : colormesh})

    @staticmethod
    def get(name):
        """ Get a node from the name """
        return NodeStorage.nodes.get(name)

class RotationControlNode(Node):
    def __init__(self, key_up, key_down, axis, angle=0, **param):
        super().__init__(**param)   # forward base constructor named arguments
        self.angle, self.axis = angle, axis
        self.key_up, self.key_down = key_up, key_down

    def draw(self, projection, view, model, win=None, **param):
        assert win is not None
        self.angle += 2 * int(glfw.get_key(win, self.key_up) == glfw.PRESS)
        self.angle -= 2 * int(glfw.get_key(win, self.key_down) == glfw.PRESS)
        self.transform = rotate(self.axis, self.angle)

        # call Node's draw method to pursue the hierarchical tree calling
        super().draw(projection, view, model, win=win, **param)

class Axis(ColorMesh):
    def __init__(self):
        self.coord = np.array(((2,0,0),(0,0,0),(0,2,0), (0,0,0),(0,0,2), (0,0,0)), np.float32)
        super().__init__([self.coord])

    def draw(self, projection, view, model, **param):
        super().draw(projection, view, model, primitive= GL.GL_LINES)
