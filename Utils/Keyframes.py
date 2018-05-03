from transform import lerp, vec
from bisect import bisect_left      # search sorted keyframe lists
from transform import (quaternion_slerp, quaternion_matrix, quaternion,
                       quaternion_from_euler, translate, rotate, scale)
from Node import Node
import glfw
class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
        keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
        self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
        self.interpolate = interpolation_function

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time < self.times[0]:
            return self.values[0]
        if time > self.times[-1]:
            return self.values[-1]

        # 2. search for closest index entry in self.times, using bisect_left function
        index = bisect_left(self.times, time)

        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        return self.interpolate(self.values[index-1], self.values[index], (time-self.times[index-1])/(self.times[index]-self.times[index-1]))

    def get_max_time(self):
        """ Return the max of the time """
        return max(self.times)



class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms
        expected rotate_keys to be quaternions
    """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale """
        self.translation_keys = KeyFrames(translate_keys)
        self.rotate_keys = KeyFrames(rotate_keys, quaternion_slerp)
        self.scale_keys = KeyFrames(scale_keys)

    def value(self, time):
        """ Compute each component's interpolation and compose TRS matrix """

        T = translate(self.translation_keys.value(time))
        R = quaternion_matrix(self.rotate_keys.value(time))
        S = scale(self.scale_keys.value(time))
        return T@R@S

    def get_duration(self):
        """ Get the duration of the animation """
        return max([self.translation_keys.get_max_time(), self.rotate_keys.get_max_time(), self.scale_keys.get_max_time()])

class KeyFrameControlNode(Node):
    """ Place node with transform keys above a controlled subtree """
    #Reset time != 0 boucle l'animation tous les resetTime
    def __init__(self, translate_keys, rotate_keys, scale_keys, resetTime=0, **kwargs):
        super().__init__(**kwargs)
        self.resetTime = None
        if resetTime != 0:
            self.resetTime = resetTime
        self.passedTime = 0
        self.keyframes = TransformKeyFrames(translate_keys, rotate_keys, scale_keys)

    def draw(self, projection, view, model, win, **param):
        """ When redraw requested, interpolate our node transform from keys """
        if glfw.get_key(win, glfw.KEY_SPACE) == glfw.PRESS:
            glfw.set_time(0)
            self.passedTime = 0

        currentTime = glfw.get_time() - self.passedTime
        if self.resetTime != None and currentTime >= self.resetTime:
            self.passedTime = glfw.get_time()
            currentTime = 0

        self.transform = self.keyframes.value(currentTime)
        super().draw(projection, view, model, **param)
