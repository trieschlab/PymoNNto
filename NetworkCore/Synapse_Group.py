from PymoNNto.NetworkCore.Base import *
import copy

import random
#def str_eval_conn(eval_string, synapses, s_id, sx, sy, sz, d_id, dx, dy, dz):
#    return eval(eval_string)

class SynapseGroup(NetworkObjectBase):

    def __init__(self, src, dst, net, tag=None, behaviour={}):
        super().__init__(tag=tag)

        if len(src.tags)>0 and len(dst.tags)>0:
            self.add_tag(src.tags[0]+' => '+dst.tags[0])

        if net is not None:
            net.SynapseGroups.append(self)
            self.network = net

        self.recording = True

        self.src = src
        self.dst = dst
        self.enabled = True
        self.group_weighting = 1

        self.behaviour = behaviour

        for k in self.behaviour:
            if self.behaviour[k].set_variables_on_init:
                self.behaviour[k].set_variables(self)


    def find_objects(self, key):
        result = []

        if key in self.behaviour:
            result.append(self.behaviour)

        for bk in self.behaviour:
            behaviour = self.behaviour[bk]
            result += behaviour[key]

        return result

    '''
    def set_connectivity(self, connectivity):
        src = self.src
        dst = self.dst
        self.enabled = self.get_synapse_mat()

        s_id = np.tile(np.arange(src.size), (1, dst.size)).reshape(dst.size, src.size)

        if hasattr(src, 'x') and hasattr(src, 'y') and hasattr(src, 'z'):
            sx = np.tile(src.x, (1, dst.size)).reshape(dst.size, src.size)
            sy = np.tile(src.y, (1, dst.size)).reshape(dst.size, src.size)
            sz = np.tile(src.z, (1, dst.size)).reshape(dst.size, src.size)

        d_id = np.tile(np.arange(dst.size), (1, src.size)).reshape(src.size, dst.size).transpose()

        if hasattr(dst, 'x') and hasattr(dst, 'y') and hasattr(dst, 'z'):
            dx = np.tile(dst.x, (1, src.size)).reshape(src.size, dst.size).transpose()
            dy = np.tile(dst.y, (1, src.size)).reshape(src.size, dst.size).transpose()
            dz = np.tile(dst.z, (1, src.size)).reshape(src.size, dst.size).transpose()

        if hasattr(src, 'width') and hasattr(dst, 'width'):  # scaling
            sxs = dst.width / src.width
            dxs = src.width / dst.width

        if hasattr(src, 'height') and hasattr(dst, 'height'):  # scaling
            sys = dst.height / src.height
            dys = src.height / dst.height

        def in_box(dist):
            x_diff=np.abs(sx-dx)
            y_diff=np.abs(sy-dy)
            z_diff=np.abs(sz-dz)
            return (x_diff<=dist)*(y_diff<=dist)*(z_diff<=dist)

        def in_circle(dist):
            x_diff=np.abs(sx-dx)
            y_diff=np.abs(sy-dy)
            z_diff=np.abs(sz-dz)
            return np.sqrt(x_diff*x_diff+y_diff*y_diff+z_diff*z_diff)<=dist

        if type(connectivity) == str:
            self.enabled = eval(connectivity)
            #print(self.enabled)
        elif type(connectivity) == float or type(connectivity) == int:
            if connectivity >= 0:
                self.enabled = (np.sqrt(
                    np.power(np.abs(sx - dx), 2) + np.power(np.abs(sy - dy), 2)) <= connectivity) * (s_id != d_id)
        else:
            self.enabled = connectivity(self, s_id, sx, sy, sz, d_id, dx, dy, dz)
    '''


    def set_var(self, key, value):
        setattr(self,key,value)
        return self

    #def add_tag(self, tag):
    #    self.tags.append(tag)
    #    return self


    def get_synapse_mat_dim(self):
        return self.dst.size, self.src.size#self.get_dest_size(), self.get_src_size()


    #def get_synapse_mat(self):
    #    return np.zeros(self.get_synapse_mat_dim())

    def get_random_synapse_mat_fixed(self, min_number_of_synapses=0):
        dim = self.get_synapse_mat_dim()
        result = np.zeros(dim)
        if min_number_of_synapses != 0:
            for i in range(dim[0]):
                synapses = np.random.choice(list(range(dim[1])), size=int(min_number_of_synapses), replace=False)
                result[i, synapses] = np.random.rand(len(synapses))
        return result#*np.random.rand(dim)

    #def get_random_synapse_mat(self, density=1.0, clone_along_first_axis=False, rnd_code=None):
    #    print("warning: use get_synapse_mat('uniform',...) instead of get_random_synapse_mat")
    #    return self.get_random_nparray((self.get_synapse_mat_dim()), density, clone_along_first_axis, rnd_code=rnd_code)*self.enabled

    def get_synapse_mat(self, mode='zeros()', scale=None, density=None, only_enabled=True, clone_along_first_axis=False, plot=False):# mode in ['zeros', 'zeros()', 'ones', 'ones()', 'uniform(...)', 'lognormal(...)', 'normal(...)']
        result = self._get_mat(mode=mode, dim=(self.get_synapse_mat_dim()), scale=scale, density=density, plot=plot)

        if clone_along_first_axis:
            result = np.array([result[0] for _ in range(self.get_synapse_mat_dim()[0])])

        if only_enabled:
            result *= self.enabled

        return result


    def get_synapse_group_size_factor(self, synapse_group, synapse_type):

        total_weighting = 0
        for s in synapse_group.dst.afferent_synapses[synapse_type]:
            total_weighting += s.group_weighting

        total = 0
        for s in synapse_group.dst.afferent_synapses[synapse_type]:
            total += s.src.size*s.src.group_weighting

        return total_weighting/total*synapse_group.src.size*synapse_group.group_weighting

    def get_distance_mat(self, radius, src_x=None, src_y=None, dst_x=None, dst_y=None):
        if src_x is None: src_x = self.src.x
        if src_y is None: src_y = self.src.y
        if dst_x is None: dst_x = self.dst.x
        if dst_y is None: dst_y = self.dst.y

        result_syn_mat = np.zeros((len(dst_x), len(src_x)))

        for d_n in range(len(dst_x)):
            dx = np.abs(src_x - dst_x[d_n])
            dy = np.abs(src_y - dst_y[d_n])

            dist = np.sqrt(dx * dx + dy * dy)
            inv_dist = np.clip(radius - dist, 0.0, None)
            inv_dist /= np.max(inv_dist)

            result_syn_mat[d_n] = inv_dist

        return result_syn_mat


    def get_ring_mat(self, radius, inner_exp, src_x=None, src_y=None, dst_x=None, dst_y=None):
        dm = self.get_distance_mat(radius, src_x, src_y, dst_x, dst_y)
        ring = np.clip(dm - np.power(dm, inner_exp)*1.5, 0.0, None)
        return ring/np.max(ring)

    def get_max_receptive_field_size(self):
        max_dx = 1
        max_dy = 1
        max_dz = 1

        #print(self.dst.x[89])

        #print(self.dst.size, self.dst.x.shape, self.dst.y.shape, self.dst.z.shape)
        #print(self.src.size, self.src.x.shape, self.src.y.shape, self.src.z.shape)

        for i in range(self.dst.size):
            if type(self.enabled) is np.ndarray:
                mask = self.enabled[i]
            else:
                mask = self.enabled

            if np.sum(mask)>0:
                x = self.dst.x[i]
                y = self.dst.y[i]
                z = self.dst.z[i]

                sx_v = self.src.x[mask]
                sy_v = self.src.y[mask]
                sz_v = self.src.z[mask]

                max_dx = np.maximum(np.max(np.abs(x-sx_v)), max_dx)
                max_dy = np.maximum(np.max(np.abs(y-sy_v)), max_dy)
                max_dz = np.maximum(np.max(np.abs(z-sz_v)), max_dz)

        return max_dx, max_dy, max_dz

    def get_sub_synapse_group(self, src_mask, dst_mask):
        result = SynapseGroup(self.src.subGroup(src_mask), self.dst.subGroup(dst_mask), net=None, behaviour={})

        # partition enabled update
        if type(self.enabled) is np.ndarray:
            mat_mask = dst_mask[:, None] * src_mask[None, :]
            result.enabled = self.enabled[mat_mask].copy().reshape(result.get_synapse_mat_dim())

        # copy al attributes
        sgd = self.__dict__
        for key in sgd:
            if key == 'behaviour':
                for k in self.behaviour:
                    result.behaviour[k] = copy.copy(self.behaviour[k])
            elif key not in ['src', 'dst', 'enabled', '_mat_eval_dict']:
                setattr(result, key, copy.copy(sgd[key]))

        return result

    '''
    def partition(self, split_size='auto'):#, receptive_field_size='auto'

        #if receptive_field_size == 'auto':
        #    receptive_field_size = self.get_max_receptive_field_size()

        if split_size == 'auto':
            best_block_size = 7
            w = int((self.src.width/best_block_size+self.dst.width/best_block_size)/2)
            h = int((self.src.height/best_block_size+self.dst.height/best_block_size)/2)
            d = int((self.src.depth / best_block_size + self.dst.depth / best_block_size) / 2)
            split_size = [np.maximum(w, 1), np.maximum(h, 1), np.maximum(d, 1)]
            if split_size[0]<3 and split_size[1]<3 and split_size[2]<3:
                return

        #print('partition:', receptive_field_size, split_size)

        self.network.partition_Synapse_Group3(self, steps=split_size)

        #self.network.partition_Synapse_Group(self, receptive_field_size=self.get_max_receptive_field_size(), split_size=split_size)
    '''

