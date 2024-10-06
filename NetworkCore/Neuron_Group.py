from PymoNNto.NetworkCore.Base_Attachable_Modules import *
from PymoNNto.NetworkBehavior.Recorder.Recorder import *
import copy

blue = (0.0, 0.0, 255.0, 255.0)
red = (255.0, 0.0, 0.0, 255.0)
green = (0.0, 200.0, 0.0, 255.0)
yellow = (255.0, 255.0, 0.0, 255.0)
purple = (255.0, 0.0, 255.0, 255.0)
aqua = (0.0, 255.0, 255.0, 255.0)
orange = (255.0, 150.0, 0.0, 255.0)
black = (0.0, 0.0, 0.0, 255.0)
white = (255.0, 255.0, 255.0, 255.0)

afferent = pre = preSynaptic = dendrite = 0
efferent = post = postSynaptic = axon = 1

class NeuronGroup(NetworkObjectBase):

    def __init__(self, net, size, behavior, tag=None, color=None):

        if tag is None and net is not None:
            tag = 'NeuronGroup_'+str(len(net.NeuronGroups)+1)

        if isinstance(size, Behavior):
            if type(behavior) is dict:
                if 0 in behavior:
                    print('warning: 0 index behavior will be overwritten by size behavior')
                behavior[0] = size
            if type(behavior) is list:
                behavior.insert(0, size)
            size = -1#will be overwritten by size-behavior

        self.size = size
        self.BaseNeuronGroup = self#used for subgroup reconstruction
        self.afferent_synapses = {} #set by SynapseGroup
        self.efferent_synapses = {}
        self.mask = True#np.array([True for _ in range(size)]).astype(bool)#True#used for subgroup reconstruction
        self.id = np.arange(self.size)

        if color is not None:
            self.color = color

        super().__init__(tag, net, behavior)
        self.add_tag('ng')

        if net is not None:
            net.NeuronGroups.append(self)
            for tag in self.tags:
                if not hasattr(net, tag):
                    setattr(net, tag, self)

    def synapses(self, mode, tag='All'):#afferent=0, efferent=1
        if mode==afferent:
            return self.afferent_synapses[tag]
        if mode==efferent:
            return self.efferent_synapses[tag]

    @property
    def def_dtype(self):
        return self.network.def_dtype

    @property
    def iteration(self):
        return self.network.iteration

    def require_synapses(self, name, afferent=True, efferent=True, warning=True):
        if afferent and not name in self.afferent_synapses:
            if warning:
                print('warning: no afferent {} synapses found'.format(name))
            self.afferent_synapses[name] = []

        if efferent and not name in self.efferent_synapses:
            if warning:
                print('warning: no efferent {} synapses found'.format(name))
            self.efferent_synapses[name] = []


    def vector(self, mode='zeros()', scale=None, density=None, plot=False):
        return self._get_mat(mode=mode, dim=(self.size), scale=scale, density=density, plot=plot)

    get_neuron_vec = vector
    vector = vector
    vec = vector
    array = vector

    def vector_buffer(self, buffer_size):
        return self.get_buffer_mat((self.size), buffer_size)

    def get_combined_synapse_shape(self, Synapse_ID):
        source_num = 0
        for syn in self.afferent_synapses[Synapse_ID]:
            d, s = syn.matrix_dim()
            source_num += s
        return self.size, source_num

    def __str__(self):
        result = 'NeuronGroup'+str(self.tags)+'('+str(self.size)+'){'
        for k in sorted(list(self.behavior.keys())):
            result += str(k) + ':' + str(self.behavior[k])
        return result+'}'

    def subGroup(self, mask=None):
        return NeuronSubGroup(self, mask)

    def group_without_subGroup(self):
        return self

    def get_masked_dict(self, dict_name, key):
        return getattr(self, dict_name)[key]

    def connected_NG_param_list(self, param_name, syn_tag='All', afferent_NGs=False, efferent_NGs=False, same_NG=False, search_behaviors=False):
        result = []

        def search_NG(NG):
            if hasattr(NG, param_name):
                attr = getattr(NG, param_name)
                if callable(attr):
                    result.append(attr(NG))
                else:
                    result.append(attr)
            if search_behaviors:
                for key, behavior in NG.behavior.items():
                    if hasattr(behavior, param_name):
                        attr = getattr(behavior, param_name)
                        if callable(attr):
                            result.append(attr(NG))
                        else:
                            result.append(attr)

        if same_NG:
            search_NG(self)

        if efferent_NGs:
            for syn in self.efferent_synapses[syn_tag]:
                search_NG(syn.dst)

        if afferent_NGs:
            for syn in self.synapses(afferent, syn_tag):
                search_NG(syn.src)

        return result

    def partition_size(self, block_size=7):
        w = block_size#int((self.src.width/block_size+self.dst.width/block_size)/2)
        h = block_size#int((self.src.height/block_size+self.dst.height/block_size)/2)
        d = block_size#int((self.src.depth / block_size + self.dst.depth / block_size) / 2)
        split_size = [np.maximum(w, 1), np.maximum(h, 1), np.maximum(d, 1)]
        if split_size[0]<2 and split_size[1]<2 and split_size[2]<2:
            return [self]
        else:
            return self.split_grid_into_sub_group_blocks(split_size)

    def partition_masks(self, steps=[1, 1, 1]):

        dst_min = [np.min(p) for p in [self.x, self.y, self.z]]
        dst_max = [np.max(p) for p in [self.x, self.y, self.z]]

        def get_start_end(step, dim):
            start=dst_min[dim]+(dst_max[dim]-dst_min[dim])/steps[dim]*step
            end=dst_min[dim]+(dst_max[dim]-dst_min[dim])/steps[dim]*(step+1)
            return start, end

        results = []

        masks = []
        for w_step in range(steps[0]):          #x_steps
            dst_x_start, dst_x_end = get_start_end(w_step, 0)
            for h_step in range(steps[1]):      #y_steps
                dst_y_start, dst_y_end = get_start_end(h_step, 1)
                for d_step in range(steps[2]):  #z_steps
                    dst_z_start, dst_z_end = get_start_end(d_step, 2)

                    sub_group_mask = (self.x >= dst_x_start) * (self.x <= dst_x_end) * (self.y >= dst_y_start) * (self.y <= dst_y_end) * (self.z >= dst_z_start) * (self.z <= dst_z_end)

                    #remove redundancies
                    for old_dst_mask in masks:
                        sub_group_mask[old_dst_mask] *= False
                    masks.append(sub_group_mask)

                    results.append(sub_group_mask)

        return results

    def split_grid_into_sub_group_blocks(self, steps=[1, 1, 1]):
        return [self.subGroup(mask) for mask in self.partition_masks(steps)]


    def get_subgroup_receptive_field_mask(self, subgroup, xyz_rf=[1,1,1]):
        rf_x, rf_y, rf_z = xyz_rf

        src_x_start = np.min(subgroup.x) - rf_x
        src_x_end = np.max(subgroup.x) + rf_x

        src_y_start = np.min(subgroup.y) - rf_y
        src_y_end = np.max(subgroup.y) + rf_y

        src_z_start = np.min(subgroup.z) - rf_z
        src_z_end = np.max(subgroup.z) + rf_z

        mask = (self.x >= src_x_start) * (self.x <= src_x_end) * (self.y >= src_y_start) * (self.y <= src_y_end) * (self.z >= src_z_start) * (self.z <= src_z_end)

        return mask

    def mask_var(self, var):
        return var

    def visualize_module(self, show_dimension=True, show_recorder=True, only_feed_forward_connections=False):
        from PymoNNto.Exploration.Visualization import Module_visualizer as drawer
        md = drawer.module_drawer()

        for k in sorted(list(self.behavior.keys())):
            b = self.behavior[k]
            b.set_gene_variables()
            if (b.__class__.__name__ != 'Recorder' or show_recorder) and (b.__class__.__name__ != 'NeuronDimension' or show_dimension):
                md.add_module(b)

        md.add_flow_chart(only_feed_forward_connections)

        md.show()


class NeuronSubGroup:

    def __init__(self, BaseNeuronGroup, mask):
        self.cache = {}
        self.key_id_cache = {}
        self.BaseNeuronGroup = BaseNeuronGroup
        self.mask = mask
        self.id_mask = np.where(mask)[0]

    def mask_var(self, var):
        if var.shape[0] != self.mask.shape[0]:
            return var[:, self.mask]
        else:
            return var[self.mask]

    def __getattr__(self, attr_name):
        if attr_name in ['BaseNeuronGroup', 'mask', 'cache', 'key_id_cache', 'id_mask']:
            return super().__getattr__(attr_name)#setattr

        if attr_name == 'size':
            return np.sum(self.mask)

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:

            if attr.shape[0] != self.mask.shape[0]:
                return attr[:, self.mask]
            else:
                return attr[self.mask]


        elif hasattr(self.BaseNeuronGroup, 'tf') and (type(attr) == self.BaseNeuronGroup.tf.python.ops.resource_variable_ops.ResourceVariable or type(attr) == self.BaseNeuronGroup.tf.python.framework.ops.EagerTensor):

            if attr.shape[0] != self.mask.shape[0]:
                return self.BaseNeuronGroup.tf.boolean_mask(attr, self.mask, axis=1)#attr[:, self.mask]
            else:
                return self.BaseNeuronGroup.tf.boolean_mask(attr, self.mask, axis=0)#attr[self.mask]
        else:
            return attr

    def __setattr__(self, attr_name, value):
        if attr_name in ['BaseNeuronGroup', 'mask', 'cache', 'key_id_cache', 'id_mask']:
            super().__setattr__(attr_name, value)
            return

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:

            if attr.shape[0] != self.mask.shape[0]:
                attr[:, self.mask] = value
            else:
                attr[self.mask] = value

        elif hasattr(self.BaseNeuronGroup, 'tf') and (type(attr) == self.BaseNeuronGroup.tf.python.ops.resource_variable_ops.ResourceVariable or type(attr) == self.BaseNeuronGroup.tf.python.framework.ops.EagerTensor):
            if attr.shape[0] != self.mask.shape[0]:
                self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [np.newaxis, self.id_mask], value)
            else:
                self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [self.id_mask], value)

        else:
            setattr(self.BaseNeuronGroup, attr, value)

    def group_without_subGroup(self):
        return self.BaseNeuronGroup
