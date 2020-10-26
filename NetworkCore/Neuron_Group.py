from NetworkCore.Base import *
from NetworkCore.Behaviour import *
from NetworkBehaviour.Recorder.Recorder import *
import copy

class NeuronGroup(NetworkObjectBase):

    def __init__(self, size, behaviour, net=None, tag=None):
        super().__init__(tag=tag)

        self.BaseNeuronGroup = self#used for subgroup reconstruction

        if isinstance(size, Behaviour):
            if type(behaviour) is dict:
                if 0 in behaviour:
                    print('warning: 0 index behaviour will be overwritten by size behaviour')
                behaviour[0] = size
            if type(behaviour) is list:
                behaviour.append(size)#first index???
            size = -1

        if net is not None:
            net.NeuronGroups.append(self)

        self.size = size
        self.afferent_synapses = {} #set by Network
        self.efferent_synapses = {}

        self.mask = True#np.array([True for _ in range(size)]).astype(np.bool)#True#used for subgroup reconstruction

        self.learning = True
        self.recording = True

        self.behaviour = {}
        if type(behaviour) == list:
            for i, b in enumerate(behaviour):
                self.behaviour[i] = copy.copy(b)
        else:
            for k in behaviour:
                self.behaviour[k] = copy.copy(behaviour[k])

        for k in self.behaviour:
            if self.behaviour[k].run_on_neuron_init_var:
                self.behaviour[k].set_variables(self)

        self.id = np.arange(self.size)


        #self.tags = []

    #do only use before initialization!!!
    #after initialization use Netork.add_behaviours_to_neuron_group(...)
    def add_behaviour(self, index, b, init=False):
        self.behaviour[index] = copy.copy(b)
        if init:
            self.behaviour[index].set_variables(self)
            self.behaviour[index].check_unused_attrs()
        return self.behaviour[index]

    def find_objects(self, key):
        result = []

        if key in self.behaviour:
            result.append(self.behaviour)

        for bk in self.behaviour:
            behaviour = self.behaviour[bk]
            result += behaviour[key]

        for syn_key in self.afferent_synapses:
            for syn in self.afferent_synapses[syn_key]:
                if syn not in result:
                    result += syn[key]

        return result

    def get_modification_value(self, key):
        result = getattr(self, key)
        if type(result) == np.ndarray:
            return np.sum(result)
        return result

    def set_modification_value(self, key, value):
        old_val = getattr(self, key)
        if type(old_val) == np.ndarray:
            mat_sum = np.sum(old_val)
            if mat_sum == 0.0:
                new = np.ones(old_val.shape)*value
            else:
                new = old_val/mat_sum*value
            print('mat set to:', new)
            return setattr(self, key, new)
        else:
            return setattr(self, key, value)

    def require_synapses(self, name, afferent=True, efferent=True, warning=True):
        if afferent and not name in self.afferent_synapses:
            if warning:
                print('warning: no afferent {} synapses found'.format(name))
            self.afferent_synapses[name] = []

        if efferent and not name in self.efferent_synapses:
            if warning:
                print('warning: no efferent {} synapses found'.format(name))
            self.efferent_synapses[name] = []

    def get_neuron_vec(self):
        return self.get_nparray((self.size))

    def get_neuron_vec_buffer(self, buffer_size):
        return self.get_buffer_mat((self.size), buffer_size)

    def get_random_neuron_vec(self, density=1.0):
        return self.get_random_nparray((self.size), density)

    #def get_shared_variables(self, name, avoid_None=True):
    #    result=[]
    #    for k in self.behaviour:
    #        val = self.behaviour[k].get_shared_variable(name)
    #        if val!=None or avoid_None==False:
    #            result.append(val)
    #    return np.array(result)

    def get_combined_synapse_shape(self, Synapse_ID):
        source_num = 0
        for syn in self.afferent_synapses[Synapse_ID]:
            d, s = syn.get_synapse_mat_dim()
            source_num += s
        return self.size, source_num

    def subGroup(self, mask=None):
        return NeuronSubGroup(self, mask)

    def group_without_subGroup(self):
        return self

    def get_masked_dict(self, dict_name, key):
        return getattr(self, dict_name)[key]

    def connected_NG_param_list(self, param_name, syn_tag='All', afferent_NGs=False, efferent_NGs=False, same_NG=False, search_behaviours=False):
        result = []

        def search_NG(NG):
            if hasattr(NG, param_name):
                attr = getattr(NG, param_name)
                if callable(attr):
                    result.append(attr(NG))
                else:
                    result.append(attr)
            if search_behaviours:
                for key, behaviour in NG.behaviour.items():
                    if hasattr(behaviour, param_name):
                        attr = getattr(behaviour, param_name)
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
            for syn in self.afferent_synapses[syn_tag]:
                search_NG(syn.src)

        return result

    def partition_size(self, block_size = 7):

        w = block_size#int((self.src.width/block_size+self.dst.width/block_size)/2)
        h = block_size#int((self.src.height/block_size+self.dst.height/block_size)/2)
        d = block_size#int((self.src.depth / block_size + self.dst.depth / block_size) / 2)
        split_size = [np.maximum(w, 1), np.maximum(h, 1), np.maximum(d, 1)]
        if split_size[0]<2 and split_size[1]<2 and split_size[2]<2:
            return [self]
        else:
            return self.partition_steps(split_size)

    def partition_steps(self, steps=[1, 1, 1]):

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

                    results.append(self.subGroup(sub_group_mask))

        return results


    def mask_var(self, var):
        return var

    '''
    def get_neuron_behaviour_parameter_list(self, neurons, param):
        result = []
        for k, b in neurons.behaviour.items():
            if hasattr(b, param):
                result.append(getattr(b, param))
        return result

    def get_connected_neuron_parameter_list(self, neurons, param, syn_tag='GLU', afferent=False, efferent=False, same_ng=False, search_behaviours=False):
        result = []
        if efferent:
            for syn in neurons.efferent_synapses[syn_tag]:
                if hasattr(syn.dst, param):
                    result.append(getattr(syn.dst, param))

        if afferent:
            for syn in neurons.afferent_synapses[syn_tag]:
                if hasattr(syn.src, param):
                    result.append(getattr(syn.src, param))

        return result
            #max_buf = max(max_buf, syn.dst.input_buffer_requirement)
        #neurons.output_buffer = neurons.get_neuron_vec_buffer(max_buf)
    '''


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

    #def get_masked_dict(self, dict_name, key):
    #    attr=getattr(self.BaseNeuronGroup, dict_name)[key]
    #    self.mask_var(attr)
    #    #if attr.shape[0] != self.mask.shape[0]:
    #    #    return attr[:, self.mask]
    #    #else:
    #    #    return attr[self.mask]

    def __getattr__(self, attr_name):
        if attr_name in ['BaseNeuronGroup', 'mask', 'cache', 'key_id_cache', 'id_mask']:
            return super().__getattr__(attr_name)#setattr

        if attr_name == 'size':
            return np.sum(self.mask)

        #print('request', attr_name,hasattr(self.BaseNeuronGroup, 'tf'))

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:

            #attr_id = id(attr)
            #if not attr_id in self.cache:
            #    if attr_name in self.key_id_cache:#remove unused cache data
            #        self.cache.pop(self.key_id_cache[attr_name])
            #    if attr.shape[0] != self.mask.shape[0]:
            #        self.cache[attr_id] = attr[:, self.mask]
            #    else:
            #        self.cache[attr_id] = attr[self.mask]
            #    self.key_id_cache[attr_name] = attr_id
            #return self.cache[attr_id]

            #self.mask_var(attr)

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

        #if len(self.BaseNeuronGroup['TF']) > 0 and not hasattr(self, 'tf'):
        #    import tensorflow as tf
        #    self.tf=tf

        #print(self.BaseNeuronGroup.__dict__)

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:

            #attr_id = id(attr)
            #if not attr_id in self.cache:
            #    if attr_name in self.key_id_cache:  # remove unused cache data
            #        self.cache.pop(self.key_id_cache[attr_name])
            #    if attr.shape[0] != self.mask.shape[0]:
            #        self.cache[attr_id] = attr[:, self.mask]
            #    else:
            #        self.cache[attr_id] = attr[self.mask]
            #    self.key_id_cache[attr_name] = attr_id
            #self.cache[attr_id] = value

            #self.mask_var(attr)[:] = value

            if attr.shape[0] != self.mask.shape[0]:
                attr[:, self.mask] = value
            else:
                attr[self.mask] = value

        elif hasattr(self.BaseNeuronGroup, 'tf') and (type(attr) == self.BaseNeuronGroup.tf.python.ops.resource_variable_ops.ResourceVariable or type(attr) == self.BaseNeuronGroup.tf.python.framework.ops.EagerTensor):
            if attr.shape[0] != self.mask.shape[0]:
                attr.assign(self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [np.newaxis, self.id_mask], value))
                #setattr(self.BaseNeuronGroup, attr_name, self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [np.newaxis, self.id_mask], value))
            else:
                #setattr(self.BaseNeuronGroup, attr_name, self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [self.id_mask], value))
                attr.assign(self.BaseNeuronGroup.tf.compat.v1.scatter_update(attr, [self.id_mask], value))


        else:
            setattr(self.BaseNeuronGroup, attr, value)

    def group_without_subGroup(self):
        return self.BaseNeuronGroup




