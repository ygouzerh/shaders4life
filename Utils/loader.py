import pyassimp                     # 3D ressource loader
import pyassimp.errors              # assimp error management + exceptions
from VertexArray import VertexArray
from Shader import Shader
import OpenGL.GL as GL              # standard Python OpenGL wrapper

import sys

sys.path.append('./Shaders')
from ShaderPos import COLOR_VERT_POS, COLOR_FRAG_POS


# -------------- 3D ressource loader -----------------------------------------
def load(file):
    """ load resources from file using pyassimp, return list of ColorMesh """
    try:
        option = pyassimp.postprocess.aiProcessPreset_TargetRealtime_MaxQuality
        scene = pyassimp.load(file, option)
    except pyassimp.errors.AssimpError:
        print('ERROR: pyassimp unable to load', file)
        return []     # error reading => return empty list

    meshes = [ColorMesh([m.vertices, m.normals], m.faces) for m in scene.meshes]
    size = sum((mesh.faces.shape[0] for mesh in scene.meshes))
    print('Loaded %s\t(%d meshes, %d faces)' % (file, len(scene.meshes), size))

    pyassimp.release(scene)
    return meshes

# -------------------------ColorMesh----------------------
class ColorMesh:
    def __init__(self, attributes, index=None):
        self.vertex_array = VertexArray(attributes, index)
        self.shader = Shader(COLOR_VERT_POS, COLOR_FRAG_POS)

    def draw(self, projection, view, model, primitive=GL.GL_TRIANGLES, color_shader=None, **param):

        names = ['view', 'projection', 'model']
        if color_shader is None:
            color_shader = self.shader

        loc = {n: GL.glGetUniformLocation(color_shader.glid, n) for n in names}
        GL.glUseProgram(color_shader.glid)
        GL.glEnable(GL.GL_CULL_FACE)

        GL.glUniformMatrix4fv(loc['view'], 1, True, view)
        GL.glUniformMatrix4fv(loc['projection'], 1, True, projection)
        GL.glUniformMatrix4fv(loc['model'], 1, True, model)

        # draw triangle as GL_TRIANGLE vertex array, draw array call
        self.vertex_array.draw(primitive)

    def set_shader_direct(self, shader):
        self.shader = shader

    def set_shader_indirect(self, vert_shader, frag_shader):
        self.shader = Shader(vert_shader, frag_shader)
