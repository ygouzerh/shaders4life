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
                        identity, quaternion, quaternion_from_euler)
from GLFWTrackball import GLFWTrackball
from Node import Node
from Textures import load_textured
from loader import load
sys.path.append('./Objects')
from Gate import Gate


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

        # initially empty list of object to draw
        self.drawables = []

        self.trackball = GLFWTrackball(self.win)
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        super().__init__(); #Init du node


    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):
            # clear draw buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # draw our scene objects
            projection = self.trackball.projection_matrix(glfw.get_window_size(self.win))
            view = self.trackball.view_matrix()
            model = identity()

            super().draw(projection, view, model, win=self.win)

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE or key == glfw.KEY_A: #Q
                glfw.set_window_should_close(self.win, True)
            if key == glfw.KEY_Z: #W
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))
            if key == glfw.KEY_SPACE:
                glfw.set_time(0)




# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    viewer = Viewer()

    skybox = load_textured("Objects/skybox/skybox.obj")[0]
    viewer.add(skybox)

    viewer.add(Gate("test",1))
    viewer.run()


if __name__ == '__main__':
    glfw.init()                # initialize window system glfw
    main()                     # main function keeps variables locally scoped
    glfw.terminate()           # destroy all glfw windows and GL contexts
