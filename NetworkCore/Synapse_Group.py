from PymoNNto.NetworkCore.Base_Attachable_Modules import *
import copy


class SynapseGroup(NetworkObjectBase):

    def __init__(self, net, src, dst, tag=None, behavior={}):

        if type(src) is str:
            s=src
            src = net[src, 0]
            if src is None:
                print(s, 'src not found for', tag)

        if type(dst) is str:
            d=dst
            dst = net[dst, 0]
            if dst is None:
                print(d, 'dst not found for', tag)

        if tag is None and net is not None:
            tag = 'SynapseGroup_'+str(len(net.SynapseGroups)+1)

        super().__init__(tag, net, behavior)
        self.add_tag('syn')

        if src is not None and dst is not None:
            if len(src.tags) > 0 and len(dst.tags) > 0:
                self.add_tag(src.tag+'_to_'+dst.tag)
        else:
            print('Warning: Not able to find source or taget for SynapseGroup '+str(self.tags))

        if net is not None:
            net.SynapseGroups.append(self)
            for tag in self.tags:
                if not hasattr(net, tag):
                    setattr(net, tag, self)

        self.recording = True

        self.src = src
        self.dst = dst
        self.enabled = True
        self.group_weighting = 1

        for ng in self.network.NeuronGroups:
            for tag in self.tags + ['All']:
                if tag not in ng.afferent_synapses:
                    ng.afferent_synapses[tag] = []
                if tag not in ng.efferent_synapses:
                    ng.efferent_synapses[tag] = []

        if self.dst.BaseNeuronGroup == self.dst: #only add to NeuronGroup not to NeuronSubGroup
            for tag in self.tags+['All']:
                self.dst.afferent_synapses[tag].append(self)

        if self.src.BaseNeuronGroup == self.src:
            for tag in self.tags+['All']:
                self.src.efferent_synapses[tag].append(self)





    def __str__(self):
        if self.network.transposed_synapse_matrix_mode:
            result = 'SynapseGroup' + str(self.tags) + '(S' + str(self.src.size) + 'xD' + str(self.dst.size) + '){'
        else:
            result = 'SynapseGroup'+str(self.tags)+'(D'+str(self.dst.size)+'xS'+str(self.src.size)+'){'
        for k in sorted(list(self.behavior.keys())):
            result += str(k) + ':' + str(self.behavior[k])+','
        return result+'}'

    def set_var(self, key, value):
        setattr(self,key,value)
        return self

    @property
    def def_dtype(self):
        return self.network.def_dtype

    @property
    def iteration(self):
        return self.network.iteration

    def matrix_dim(self):
        if self.network.transposed_synapse_matrix_mode:
            return self.src.size, self.dst.size
        else:
            return self.dst.size, self.src.size

    def get_random_synapse_mat_fixed(self, min_number_of_synapses=0):
        dim = self.matrix_dim()
        result = np.zeros(dim)
        if min_number_of_synapses != 0:
            for i in range(dim[0]):
                synapses = np.random.choice(list(range(dim[1])), size=int(min_number_of_synapses), replace=False)
                result[i, synapses] = np.random.rand(len(synapses))
        return result#*np.random.rand(dim)

    def matrix(self, mode='zeros()', scale=None, density=None, plot=False):
        return self._get_mat(mode=mode, dim=(self.matrix_dim()), scale=scale, density=density, plot=plot)

    matrix = matrix
    mat = matrix
    get_synapse_mat = matrix

    def get_synapse_group_size_factor(self, synapse_group, synapse_type):

        total_weighting = 0
        for s in synapse_group.dst.synapses(afferent, synapse_type):
            total_weighting += s.group_weighting

        total = 0
        for s in synapse_group.dst.synapses(afferent, synapse_type):
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
        result = SynapseGroup(self.src.subGroup(src_mask), self.dst.subGroup(dst_mask), net=None, behavior={})

        # partition enabled update
        if type(self.enabled) is np.ndarray:
            mat_mask = dst_mask[:, None] * src_mask[None, :]
            result.enabled = self.enabled[mat_mask].copy().reshape(result.matrix_dim())

        # copy al attributes
        sgd = self.__dict__
        for key in sgd:
            if key == 'behavior':
                for k in self.behavior:
                    result.behavior[k] = copy.copy(self.behavior[k])
            elif key not in ['src', 'dst', 'enabled', '_mat_eval_dict']:
                setattr(result, key, copy.copy(sgd[key]))

        return result

    def ignore_transpose_mode(self, W):# always returns DxS matrix
        if self.network.transposed_synapse_matrix_mode:
            return W.T
        else:
            return W

