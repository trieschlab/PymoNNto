from NetworkCore.Base import *
from NetworkCore.Neuron_Behaviour import *
from NetworkBehaviour.Recorder.Recorder import *
import copy

class NeuronGroup(NetworkObjectBase):

    def __init__(self, size, behaviour, net=None, tag=None):
        super().__init__(tag=tag)

        self.BaseNeuronGroup = self#used for subgroup reconstruction

        if isinstance(size, Neuron_Behaviour):
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

    def require_synapses(self, name):
        if not name in self.afferent_synapses:
            print('warning: no {} synapses found'.format(name))
            self.afferent_synapses[name] = []

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
        return TRENNeuronSubGroup(self, mask)

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


class TRENNeuronSubGroup:

    def __init__(self, BaseNeuronGroup, mask):
        self.cache = {}
        self.key_id_cache = {}
        self.BaseNeuronGroup = BaseNeuronGroup
        self.mask = mask

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
        if attr_name in ['BaseNeuronGroup', 'mask', 'cache', 'key_id_cache']:
            return super().__getattr__(attr_name)#setattr

        if attr_name == 'size':
            return np.sum(self.mask)

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

        else:
            return attr

    def __setattr__(self, attr_name, value):
        if attr_name in ['BaseNeuronGroup', 'mask', 'cache', 'key_id_cache']:
            super().__setattr__(attr_name, value)
            return

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



        else:
            setattr(self.BaseNeuronGroup, attr, value)

    def group_without_subGroup(self):
        return self.BaseNeuronGroup




