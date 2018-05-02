from loader import load
from Node import Node
from transform import (translate, rotate, scale)

class Gate(Node):


    def __init__(self, name, height):
            super().__init__(name)

            cylinder = load("Objects/cylinder.obj")[0]
            cube = load("Objects/cube/cube.obj")[0]


            charniereLeft = Node(children=[cube],transform=translate(5,0,0)@scale(11,2,0.7))
            charniereRight = Node(children=[cube], transform=translate(-5,0,0)@scale(11,2,0.7))
            nodeLeft = Node(children=[cylinder, charniereLeft], transform=translate(-1,0,0)@scale(0.1,height,0.1))
            nodeRight = Node(children=[cylinder, charniereRight],transform=translate(1,0,0)@scale(0.1,height,0.1))
            self.add(nodeLeft,nodeRight)
