from PymoNNto.NetworkBehavior.Structure.Structure import *
from PymoNNto.NetworkCore.Behavior import *
from PymoNNto.NetworkCore.Synapse_Group import *


class Remove_Autapses(Behavior):
    initialize_on_init = True

    def initialize(self, synapses):
        src = synapses.src
        dst = synapses.dst

        s_id = np.tile(np.arange(src.size), (1, dst.size)).reshape(dst.size, src.size)
        d_id = np.tile(np.arange(dst.size), (1, src.size)).reshape(src.size, dst.size).transpose()

        synapses.enabled *= (s_id != d_id)


class Receptive_Fields(Behavior):
    visualization_module_inputs = ['s.src.x', 's.src.y', 's.src.z', 's.dst.x', 's.dst.y', 's.dst.z']

    initialize_on_init = True

    def get_enabled_mat(self, synapses, s_id, sx, sy, sz, d_id, dx, dy, dz):
        print('not implemented. Please use inherited classes below.')
        return synapses.enabled

    def initialize(self, synapses):
        src = synapses.src
        dst = synapses.dst
        #synapses.enabled = synapses.matrix()

        s_id = np.tile(np.arange(src.size), (1, dst.size)).reshape(dst.size, src.size)#vec_to_mat(np.arange(src.size), dst.size) #

        sx = None
        sy = None
        sz = None

        if hasattr(src, 'x') and hasattr(src, 'y') and hasattr(src, 'z'):
            #sx = vec_to_mat(src.x, dst.size)
            #sy = vec_to_mat(src.y, dst.size)
            #sz = vec_to_mat(src.z, dst.size)

            sx = np.tile(src.x, (1, dst.size)).reshape(dst.size, src.size)
            sy = np.tile(src.y, (1, dst.size)).reshape(dst.size, src.size)
            sz = np.tile(src.z, (1, dst.size)).reshape(dst.size, src.size)

        d_id = np.tile(np.arange(dst.size), (1, src.size)).reshape(src.size, dst.size).transpose()

        dx = None
        dy = None
        dz = None

        if hasattr(dst, 'x') and hasattr(dst, 'y') and hasattr(dst, 'z'):
            dx = np.tile(dst.x, (1, src.size)).reshape(src.size, dst.size).transpose()
            dy = np.tile(dst.y, (1, src.size)).reshape(src.size, dst.size).transpose()
            dz = np.tile(dst.z, (1, src.size)).reshape(src.size, dst.size).transpose()

        synapses.enabled *= self.get_enabled_mat(synapses, s_id, sx, sy, sz, d_id, dx, dy, dz)

        if self.parameter('remove_autapses', False):
            synapses.enabled *= (s_id != d_id)


class Box_Receptive_Fields(Receptive_Fields):

    def get_enabled_mat(self, synapses, s_id, sx, sy, sz, d_id, dx, dy, dz):
        range=self.parameter('range', None, required=True)
        if sx is not None and sy is not None and sz is not None and dx is not None and dy is not None and dz is not None:
            x_diff = np.abs(sx - dx)
            y_diff = np.abs(sy - dy)
            z_diff = np.abs(sz - dz)
            return (x_diff <= range) * (y_diff <= range) * (z_diff <= range)
        else:
            print('Neuron needs x,y and z vectors to create receptive fields')
            return synapses.enabled

class Circle_Receptive_Fields(Receptive_Fields):

    def get_enabled_mat(self, synapses, s_id, sx, sy, sz, d_id, dx, dy, dz):
        radius = self.parameter('radius', None, required=True)
        if sx is not None and sy is not None and sz is not None and dx is not None and dy is not None and dz is not None:
            x_diff = np.abs(sx - dx)
            y_diff = np.abs(sy - dy)
            z_diff = np.abs(sz - dz)
            return np.sqrt(x_diff * x_diff + y_diff * y_diff + z_diff * z_diff) <= radius
        else:
            print('Neuron needs x,y and z vectors to create receptive fields')
            return synapses.enabled

#r = Circle_Receptive_Fields()
#r.visualize_module()
