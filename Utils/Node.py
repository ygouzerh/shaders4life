from transform import identity, rotate
import glfw
from loader import ColorMesh
import numpy as np
import OpenGL.GL as GL
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat)

class Node:
    """ Scene graph transform and parameter broadcast node """
    number_subnodes = 0
    def __init__(self, name='', transform=identity(), children=(), **param):
        self.transform, self.param, self.name = transform, param, name
        self.children = dict()
        self.add(*children)
        self.add(Axis())# Fait bugger le skinning

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        for child in drawables:
            if(isinstance(child, Node)):
                self.children.update({child.name : child})
                NodeStorage.add_node(child)
            else:
                self.children.update({"ColorMeshLocal"+str(Node.number_subnodes) : child})
                NodeStorage.add_colormesh(child)
            Node.number_subnodes += 1

    def draw(self, projection, view, model, **param):
        """ Recursive draw, passing down named parameters & model matrix. """
        # merge named parameters given at initialization with those given here
        param = dict(param, **self.param)
        model =  model @ self.transform
        for childname, child in self.children.items():
            child.draw(projection, view, model, **param)

    def translate(self, x=0.0, y=0.0, z=0.0):
        """ Translate the node """
        self.transform =  translate(x, y, z) @ self.transform

    def scale(self, x, y=None, z=None):
        """ Scale the node """
        self.transform = scale(x, y, z) @ self.transform

    def rotate(self, axis=(1., 0., 0.), angle=0.0, radians=None):
        """ Rotate the node : warning, it's not using quaternion """
        self.transform = rotate(axis, angle, radians) @ self.transform

    def set_global_position(self, x=0.0, y=0.0, z=0.0):
        """ Reset global position """
        self.transform = translate(x, y , z)

class NodeStorage:
    """ HashMap to interact easily with all the nodes """
    nodes = dict()

    @staticmethod
    def add_node(node):
        """ Add one node """
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
