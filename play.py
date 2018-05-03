#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""
# Python built-in modules
import os                           # os function, i.e. checking file status
import sys
import json

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
from itertools import cycle

sys.path.append('./Utils')
from transform import (translate, rotate, scale, vec, frustum, perspective,
                        identity, quaternion, quaternion_from_euler, lookat)
from world import MapCube, Map
from Shader import Shader
from loader import load
from Node import Node, RotationControlNode, NodeStorage, Axis
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

    def __init__(self, width=640, height=480, map_width=60, map_height=60, map_depth=60):
        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)
        self.win = glfw.create_window(width, height, 'Viewer', None, None)
        # glfw.maximize_window(self.win)
        # self.add(self.terrain.create())
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
        self.terrain = Map(map_width, map_height, map_depth)
        self.add(self.terrain.create())

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
            if key == glfw.KEY_O:
                NodeStorage.get("player").reset_time()
            if key == glfw.KEY_W:
                self.trackball.translate_easy(0, 0, 1)
            if key == glfw.KEY_S:
                self.trackball.translate_easy(0, 0, -1)
            if key == glfw.KEY_DOWN:
                self.trackball.translate_easy(0, 1, 0)
            if key == glfw.KEY_UP:
                self.trackball.translate_easy(0, -1, 0)
            if key == glfw.KEY_A:
                self.trackball.rotate_easy((0, 1, 0), -2)
            if key == glfw.KEY_D:
                self.trackball.rotate_easy((0, 1, 0), 2)
            if key == glfw.KEY_LEFT:
                self.trackball.rotate_easy((1, 0, 0), -2)
            if key == glfw.KEY_RIGHT:
                self.trackball.rotate_easy((1, 0, 0), 2)
            if key == glfw.KEY_B:
                player = NodeStorage.get("player")
                player.transform = self.trackball.view_matrix()
            if key == glfw.KEY_N:
                self.trackball.reset_rotation()
            if key == glfw.KEY_M:
                self.trackball.reset_hard()
            if key == glfw.KEY_Y:
                NodeStorage.get("player_node").translate(0, 0, -0.5)
                self.terrain.elevate(NodeStorage.get("player_node"))
            if key == glfw.KEY_G:
                NodeStorage.get("player_node").rotate((0, 1, 0), -2)
                self.terrain.elevate(NodeStorage.get("player_node"))
            if key == glfw.KEY_H:
                NodeStorage.get("player_node").translate(0, 0, 0.5)
                self.terrain.elevate(NodeStorage.get("player_node"))
            if key == glfw.KEY_J:
                NodeStorage.get("player_node").rotate((0, 1, 0), 2)
                self.terrain.elevate(NodeStorage.get("player_node"))

    def set_terrain(self, terrain):
        """
            Set the terrain
            Warning : do immediately after the initialization.
            Not before because to create the map we need first to create
            the viewer
        """
        self.terrain = terrain

# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer(map_width=400, map_height=400, map_depth=400)
    viewer.add()
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
