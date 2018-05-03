from PIL import Image               # load images for textures
from itertools import cycle
import OpenGL.GL as GL              # standard Python OpenGL wrapper
from Shader import Shader
import numpy as np
from VertexArray import VertexArray
import glfw                         # lean window system wrapper for OpenGL
import sys
import pyassimp                     # 3D ressource loader
import os
from Node import Node
from perlin_noise import perlinText

# -------------- OpenGL Texture Wrapper ---------------------------------------
class Texture:
    """ Helper class to create and automatically destroy textures """
    def __init__(self, file, wrap_mode=GL.GL_REPEAT, min_filter=GL.GL_LINEAR,
                 mag_filter=GL.GL_LINEAR_MIPMAP_LINEAR):
        self.glid = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.glid)
        # helper array stores texture format for every pixel size 1..4
        format = [GL.GL_LUMINANCE, GL.GL_LUMINANCE_ALPHA, GL.GL_RGB, GL.GL_RGBA]
        try:
            # imports image as a numpy array in exactly right format
            tex = np.array(Image.open(file))
            format = format[0 if len(tex.shape) == 2 else tex.shape[2] - 1]
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, tex.shape[1],
                            tex.shape[0], 0, format, GL.GL_UNSIGNED_BYTE, tex)

            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, wrap_mode)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, wrap_mode)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, min_filter)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, mag_filter)
            GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
            message = 'Loaded texture %s\t(%s, %s, %s, %s)'
            print(message % (file, tex.shape, wrap_mode, min_filter, mag_filter))
        except FileNotFoundError:
            print("ERROR: unable to load texture file %s" % file)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)

class TexturePerlin:
    """ Helper class to create and automatically destroy textures """
    def __init__(self, wrap_mode=GL.GL_REPEAT, min_filter=GL.GL_LINEAR,
                 mag_filter=GL.GL_LINEAR_MIPMAP_LINEAR):
        self.glid = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.glid)
        # helper array stores texture format for every pixel size 1..4
        format = [GL.GL_LUMINANCE, GL.GL_LUMINANCE_ALPHA, GL.GL_RGB, GL.GL_RGBA]
        tex = np.array(perlinText(200,200))
        format = format[0 if len(tex.shape) == 2 else tex.shape[2] - 1]
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, tex.shape[1],
                        tex.shape[0], 0, format, GL.GL_UNSIGNED_BYTE, tex)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, wrap_mode)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, wrap_mode)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, min_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, mag_filter)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
        message = 'Loaded texture %s\t(%s, %s, %s, %s)'
        print(message % ("Perlin", tex.shape, wrap_mode, min_filter, mag_filter))
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)


# -------------- Example texture plane class ----------------------------------
TEXTURE_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
out vec2 fragTexCoord;
void main() {
    gl_Position = modelviewprojection * vec4(position, 1);
    fragTexCoord = position.xy;
}"""

TEXTURE_FRAG = """#version 330 core
uniform sampler2D diffuseMap;
in vec2 fragTexCoord;
out vec4 outColor;
void main() {
    outColor = texture(diffuseMap, fragTexCoord);
}"""

class TexturedPerlinPlane:
    """ Simple first textured object """

    def __init__(self):
        # feel free to move this up in the viewer as per other practicals
        self.shader = Shader(TEXTURE_VERT, TEXTURE_FRAG)

        # triangle and face buffers
        vertices = 100 * np.array(((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)), np.float32)
        faces = np.array(((0, 1, 2), (0, 2, 3)), np.uint32)
        self.vertex_array = VertexArray([vertices], faces)

        # interactive toggles
        self.wrap = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                           GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filter = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                             (GL.GL_LINEAR, GL.GL_LINEAR),
                             (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap_mode, self.filter_mode = next(self.wrap), next(self.filter)

        # setup texture and upload it to GPU
        self.texture = TexturePerlin(self.wrap_mode, *self.filter_mode)
        self.pressable = [False, False] #C MOI KI LA FE CLOCHETEU

    def draw(self, projection, view, model, win=None, **_kwargs):
        # some interactive elements
        if glfw.get_key(win, glfw.KEY_F6) == glfw.RELEASE:
            self.pressable[0] = True
        if glfw.get_key(win, glfw.KEY_F7) == glfw.RELEASE:
            self.pressable[1] = True
        if self.pressable[0] and glfw.get_key(win, glfw.KEY_F6) == glfw.PRESS:
            self.pressable[0] = False
            self.wrap_mode = next(self.wrap)
            self.texture = TexturePerlin(self.wrap_mode, *self.filter_mode)

        if self.pressable[1] and glfw.get_key(win, glfw.KEY_F7) == glfw.PRESS:
            self.pressable[1] = False
            self.filter_mode = next(self.filter)
            self.texture = TexturePerlin(self.wrap_mode, *self.filter_mode)

        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)
        self.vertex_array.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)


class TexturedPlane:
    """ Simple first textured object """

    def __init__(self, file):
        # feel free to move this up in the viewer as per other practicals
        self.shader = Shader(TEXTURE_VERT, TEXTURE_FRAG)

        # triangle and face buffers
        vertices = 100 * np.array(((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)), np.float32)
        faces = np.array(((0, 1, 2), (0, 2, 3)), np.uint32)
        self.vertex_array = VertexArray([vertices], faces)

        # interactive toggles
        self.wrap = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                           GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filter = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                             (GL.GL_LINEAR, GL.GL_LINEAR),
                             (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap_mode, self.filter_mode = next(self.wrap), next(self.filter)
        self.file = file

        # setup texture and upload it to GPU
        self.texture = Texture(file, self.wrap_mode, *self.filter_mode)
        self.pressable = [False, False]

    def draw(self, projection, view, model, win=None, **_kwargs):

        # some interactive elements
        if glfw.get_key(win, glfw.KEY_F6) == glfw.RELEASE:
            self.pressable[0] = True
        if glfw.get_key(win, glfw.KEY_F7) == glfw.RELEASE:
            self.pressable[1] = True
        if self.pressable[0] and glfw.get_key(win, glfw.KEY_F6) == glfw.PRESS:
            self.pressable[0] = False
            self.wrap_mode = next(self.wrap)
            self.texture = Texture(self.file, self.wrap_mode, *self.filter_mode)

        if self.pressable[1] and glfw.get_key(win, glfw.KEY_F7) == glfw.PRESS:
            self.pressable[1] = False
            self.filter_mode = next(self.filter)
            self.texture = Texture(self.file, self.wrap_mode, *self.filter_mode)

        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'diffuseMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)
        self.vertex_array.draw(GL.GL_TRIANGLES)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)

TEXTURE_FILE_VERT = """#version 330 core
uniform mat4 modelviewprojection;
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texPosition;

out vec2 fragTexCoord;
void main() {
    fragTexCoord = texPosition;
    gl_Position = modelviewprojection * vec4(position, 1);
}"""

TEXTURE_FILE_FRAG = """#version 330 core
uniform sampler2D texMap;
in vec2 fragTexCoord;

out vec4 outColor;
void main() {
    outColor = texture(texMap, fragTexCoord);
}"""
class PerlinMesh:
    def __init__(self, mesh):
        self.mesh = mesh
        self.mesh.shader = Shader(TEXTURE_VERT, TEXTURE_FRAG)

        # setup texture and upload it to GPU
        self.texture = TexturePerlin(GL.GL_REPEAT)

    def draw(self, projection, view, model, win=None, primitive=GL.GL_TRIANGLES, **param):
        if win is None:
            print("Win not defined!")
            return

        GL.glUseProgram(self.mesh.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.mesh.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.mesh.shader.glid, 'texMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)


        self.mesh.vertex_array.draw(primitive)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)


class TexturedMesh:
    def __init__(self, texture, attributes, indices):
        self.vertex_array = VertexArray(attributes, indices)
        self.shader = Shader(TEXTURE_FILE_VERT, TEXTURE_FILE_FRAG)
        # interactive toggles
        self.wrap = cycle([GL.GL_REPEAT, GL.GL_MIRRORED_REPEAT,
                           GL.GL_CLAMP_TO_BORDER, GL.GL_CLAMP_TO_EDGE])
        self.filter = cycle([(GL.GL_NEAREST, GL.GL_NEAREST),
                             (GL.GL_LINEAR, GL.GL_LINEAR),
                             (GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR)])
        self.wrap_mode, self.filter_mode = next(self.wrap), next(self.filter)
        self.file = texture

        # setup texture and upload it to GPU
        self.texture = Texture(texture, self.wrap_mode, *self.filter_mode)
        self.pressable = [False, False] #C MOI KI LA FE CLOCHETEU

    def draw(self, projection, view, model, win=None, primitive=GL.GL_TRIANGLES, **param):
        if win is None:
            print("Win not defined!")
            return
        # some interactive elements
        if glfw.get_key(win, glfw.KEY_F6) == glfw.RELEASE:
            self.pressable[0] = True
        if glfw.get_key(win, glfw.KEY_F7) == glfw.RELEASE:
            self.pressable[1] = True
        if self.pressable[0] and glfw.get_key(win, glfw.KEY_F6) == glfw.PRESS:
            self.pressable[0] = False
            self.wrap_mode = next(self.wrap)
            self.texture = Texture(self.file, self.wrap_mode, *self.filter_mode)

        if self.pressable[1] and glfw.get_key(win, glfw.KEY_F7) == glfw.PRESS:
            self.pressable[1] = False
            self.filter_mode = next(self.filter)
            self.texture = Texture(self.file, self.wrap_mode, *self.filter_mode)



        GL.glUseProgram(self.shader.glid)

        # projection geometry
        loc = GL.glGetUniformLocation(self.shader.glid, 'modelviewprojection')
        GL.glUniformMatrix4fv(loc, 1, True, projection @ view @ model)

        # texture access setups
        loc = GL.glGetUniformLocation(self.shader.glid, 'texMap')
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.glid)
        GL.glUniform1i(loc, 0)


        self.vertex_array.draw(primitive)

        # leave clean state for easier debugging
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glUseProgram(0)
        # -------------- 3D textured mesh loader ---------------------------------------
def load_textured(file):
    """ load resources using pyassimp, return list of TexturedMeshes """
    try:
        option = pyassimp.postprocess.aiProcessPreset_TargetRealtime_MaxQuality
        scene = pyassimp.load(file, option)
    except pyassimp.errors.AssimpError:
        print('ERROR: pyassimp unable to load', file)
        return []  # error reading => return empty list

    # Note: embedded textures not supported at the moment
    path = os.path.dirname(file)
    path = os.path.join('.', '') if path == '' else path
    for mat in scene.materials:
        mat.tokens = dict(reversed(list(mat.properties.items())))
        if 'file' in mat.tokens:  # texture file token
            tname = mat.tokens['file'].split('/')[-1].split('\\')[-1]
            # search texture in file's whole subdir since path often screwed up
            tname = [os.path.join(d[0], f) for d in os.walk(path) for f in d[2]
                     if tname.startswith(f) or f.startswith(tname)]
            if tname:
                mat.texture = tname[0]
            else:
                print('Failed to find texture:', tname)

    # prepare textured mesh
    meshes = []
    for mesh in scene.meshes:
        texture = scene.materials[mesh.materialindex].texture

        # tex coords in raster order: compute 1 - y to follow OpenGL convention
        tex_uv = ((0, 1) + mesh.texturecoords[0][:, :2] * (1, -1)
                  if mesh.texturecoords.size else None)
        # create the textured mesh object from texture, attributes, and indices
        meshes.append(TexturedMesh(texture, [mesh.vertices, tex_uv], mesh.faces))

    size = sum((mesh.faces.shape[0] for mesh in scene.meshes))
    print('Loaded %s\t(%d meshes, %d faces)' % (file, len(scene.meshes), size))

    pyassimp.release(scene)
    return meshes
