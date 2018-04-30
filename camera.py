#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
import sys

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from itertools import cycle

sys.path.append('./Utils')
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat)
from Shader import Shader
from loader import load
from Node import Node, RotationControlNode, NodeStorage
from GLFWTrackball import GLFWTrackball
from Node import Node
from Keyframes import KeyFrames, TransformKeyFrames, KeyFrameControlNode
from Skinning import SkinnedCylinder, load_skinned
sys.path.append('./Objects')
from Textures import TexturedPlane, load_textured
sys.path.append('./Shaders')
from ShaderPos import COLOR_VERT_POS, COLOR_FRAG_POS



# ------------  Viewer class & window management ------------------------------
class Viewer(Node):
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, width=640, height=480):
        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # register event handlersVertexProf
        glfw.set_key_callback(self.win, self.on_key)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glClearColor(0.1, 0.1, 0.1, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        # compile and initialize shader programs once globally
        #self.color_shader = Shader(COLOR_VERT, COLOR_FRAG)

        # initially empty list of object to draw
        self.drawables = []

        self.trackball = GLFWTrackball(self.win)
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])
        GL.glEnable(GL.GL_DEPTH_TEST) #Maxime t

        super().__init__(); #Init du node
        self.x = 0
        self.y = 0
        self.z = 10

    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            # draw our scene objects
            projection = self.trackball.projection_matrix(glfw.get_window_size(self.win))
            view = self.trackball.view_matrix()
            model = identity()
            # NodeStorage.get("cube1")
            super().draw(projection, view, model, win=self.win)

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(self.win, True)
            if key == glfw.KEY_Z: #W
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))
            if key == glfw.KEY_SPACE:
                glfw.set_time(0)
            if key == glfw.KEY_W:
                self.trackball.translate_easy(0, 0, 1)
            if key == glfw.KEY_S:
                self.trackball.translate_easy(0, 0, -1)
            if key == glfw.KEY_A:
                self.trackball.rotate_easy((0, 1, 0), 2)
            if key == glfw.KEY_D:
                self.trackball.rotate_easy((0, 1, 0), -2)
            if key == glfw.KEY_UP:
                self.trackball.rotate_easy((1, 0, 0), -2)
            if key == glfw.KEY_DOWN:
                self.trackball.rotate_easy((1, 0, 0), 2)
            if key == glfw.KEY_E:
                NodeStorage.get("cube1").translate(0, 0, -0.5)
            if key == glfw.KEY_R:
                NodeStorage.get("cube1").rotate((0, 0, 1), 2)







# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()
    # cube = load_textured("Objects/skybox/skybox.obj")[0]
    unCube = load("Objects/cube/cube.obj")[0]
    cube_node = Node("cube1");
    cube_node.add(unCube)
    cube_node.set_global_position(2, 2, -2)
    # cube_node_2 = Node("cube2");
    # cube_node_2.add(unCube)
    # cube_node_2.set_global_position(-1, 2, -2)
    # cube_node_3 = Node("cube3");
    # cube_node_3.add(unCube)
    # cube_node_3.set_global_position(-1, -2, -2)
    # cube_node_4 = Node("cube4");
    # cube_node_4.add(unCube)
    # cube_node_4.set_global_position(1, -2, -2)
    # viewer.add(cylinder_node)
    # WARNING : The arm use the same touchs
    viewer.add(cube_node)
    # viewer.add(TexturedPlane("Textures/grass.png"))
    #unLapinAvecUneOmbre = LambertianMesh((1,0.3,0.5),(1,1,1),uri="Objects/bunny/bunny.obj")
    #unLapin = load_textured("Objects/bunny/bunny.obj")[0]
    #suzanne = load("Objects/suzanne.obj")[0]
    #viewer.add(RotatingObject(unLapin, (0,0.5,0)))
    #translate_keys = {0: vec(0, 0, 0), 2: vec(1, 1, 0), 4: vec(0, 0, 0)}
    #rotate_keys = {0: quaternion(), 2: quaternion_from_euler(180, 45, 90),
    #               3: quaternion_from_euler(180, 0, 180), 4: quaternion()}
    #scale_keys = {0: 1, 2: 0.5, 4: 1,300:100}
    #keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys)
    #keynode.add(load("Objects/cylinder.obj")[0])
    #viewer.add(keynode)

    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts