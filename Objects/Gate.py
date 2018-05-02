from loader import load
from Node import Node, Axis, RotationControlNode
from transform import (translate, rotate, scale, vec, quaternion, quaternion_from_euler)
from Keyframes import KeyFrameControlNode
import glfw

class Gate(Node):


    def __init__(self, name, height):
            super().__init__(name)

            cylinder = load("Objects/cylinder.obj")[0]
            cube = load("Objects/cube/cube.obj")[0]

            door_left = Node(children=[cube],transform=translate(5,0,0)@scale(10,2,0.7))
            scale_left = Node(children=[cylinder, door_left], transform=scale(0.1,height,0.1))
            rotation_left = RotationControlNode( glfw.KEY_DOWN, glfw.KEY_UP,vec(0,1,0), speed=0.5, children=[scale_left])
            node_left = Node(children=[rotation_left], transform=translate(-1,0,0))

            door_right = Node(children=[cube],transform=translate(-5,0,0)@scale(10,2,0.7))
            scale_right = Node(children=[cylinder, door_right], transform=scale(0.1,height,0.1))
            rotation_right = RotationControlNode( glfw.KEY_DOWN, glfw.KEY_UP,vec(0,-1,0), speed=0.5, children=[scale_right])
            node_right = Node(children=[rotation_right], transform=translate(1,0,0))

            self.add(node_left, node_right)
