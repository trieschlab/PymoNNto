from PymoNNto.NetworkCore.Behaviour import *
import math
import numpy as np


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def get_squared_dim(number_of_neurons, depth=1, round_up=True):

    divider=int(np.trunc(np.sqrt(number_of_neurons)))

    while divider>1 and number_of_neurons%divider!=0:
      divider-=1

    w=divider
    h=int(number_of_neurons/divider)

    print('set network size to', w, 'x', h)
    return NeuronDimension(width=w, height=h, depth=depth)


class NeuronDimension(Behaviour):

    set_variables_on_init = True

    #def __init__(self, width=1, height=1, depth=1):
    #    super().__init__()

    def set_positions(self, width=1, height=1, depth=1):
        self.neurons.x = np.array([i%width for i in range(self.neurons.size)]).astype(def_dtype)
        self.neurons.y = np.array([np.floor(i/width)%height for i in range(self.neurons.size)]).astype(def_dtype)
        self.neurons.z = np.array([np.floor(i/(width*height)) for i in range(self.neurons.size)]).astype(def_dtype)

    def apply_pattern_transformation_function(self, transform_mat, hup, wup, depth):

        big_x_mat = np.tile(np.arange(wup), (1, hup)).reshape(1, hup, wup)
        big_y_mat = np.tile(np.arange(wup), (1, hup)).reshape(1, hup, wup).transpose()

        big_x_mat = np.repeat(big_x_mat[:, :, :], depth, axis=0).flatten()
        big_y_mat = np.repeat(big_y_mat[:, :, :], depth, axis=0).flatten()

        self.neurons.x = big_x_mat[transform_mat]
        self.neurons.y = big_y_mat[transform_mat]

    def move(self, x=0, y=0, z=0):
        self.neurons.x += x
        self.neurons.y += y
        self.neurons.z += z
        return self

    def scale(self, x=1, y=1, z=1):
        self.neurons.x *= x
        self.neurons.y *= y
        self.neurons.z *= z
        return self

    def noise(self, x_noise=1, y_noise=1, z_noise=1, centered=True):
        self.neurons.x += np.random.rand(len(self.neurons.x)) * x_noise
        self.neurons.y += np.random.rand(len(self.neurons.y)) * y_noise
        self.neurons.z += np.random.rand(len(self.neurons.z)) * z_noise

        if centered:
            self.neurons.x -= x_noise / 2
            self.neurons.y -= y_noise / 2
            self.neurons.z -= z_noise / 2
        return self

    def rotate(self, axis, theta):
        for i in range(self.size):
            self.neurons.x[i], self.neurons.y[i], self.neurons.z[i] = np.dot(rotation_matrix(axis, theta), [self.neurons.x[i], self.neurons.y[i], self.neurons.z[i]])
        return self

    #def stretch_to_equal_size(self, target_neurons):
    #    if hasattr(target_neurons, 'width') and self.neurons.width>0:
    #        x_stretch = target_neurons.width/self.neurons.width
    #        self.neurons.x *= x_stretch

    #    if hasattr(target_neurons, 'height') and self.neurons.height > 0:
    #        y_stretch = target_neurons.height/self.neurons.height
    #        self.neurons.y *= y_stretch

    #    if hasattr(target_neurons, 'depth') and self.neurons.depth > 0:
    #        z_stretch = target_neurons.depth/self.neurons.depth
    #        self.neurons.z *= z_stretch

    def stretch_to_equal_size(self, target_neurons):

        if hasattr(target_neurons, 'width') and self.neurons.width>0:
            x_stretch = target_neurons.width/self.neurons.width
            self.neurons.x *= x_stretch

        if hasattr(target_neurons, 'height') and self.neurons.height > 0:
            y_stretch = target_neurons.height/self.neurons.height
            self.neurons.y *= y_stretch

        if hasattr(target_neurons, 'depth') and self.neurons.depth > 0:
            z_stretch = target_neurons.depth/self.neurons.depth
            self.neurons.z *= z_stretch


    def set_variables(self, neurons):
        self.add_tag('structure')

        self.width = self.get_init_attr('width', 1, neurons)
        self.height = self.get_init_attr('height', 1, neurons)
        self.depth = self.get_init_attr('depth', 1, neurons)

        for pg in self.get_init_attr('input_patterns', [], neurons):
            dim = pg.get_pattern_dimension()#.reconstruct_pattern(None)
            if len(dim) > 0: self.height = np.maximum(self.height, dim[0])
            if len(dim) > 1: self.width = np.maximum(self.width, dim[1])
            if len(dim) > 2:
                self.depth = np.maximum(self.depth, dim[0])
                self.height = np.maximum(self.height, dim[1])
                self.width = np.maximum(self.width, dim[2])

        self.neurons=neurons
        neurons.width = self.width
        neurons.height = self.height
        neurons.depth = self.depth
        neurons.size=self.width*self.height*self.depth
        self.set_positions(self.width, self.height, self.depth)
        if self.get_init_attr('centered', True, neurons):
            self.move(-(self.width-1)/2,-(self.height-1)/2,-(self.depth-1)/2)

    def new_iteration(self, neurons):
        return




