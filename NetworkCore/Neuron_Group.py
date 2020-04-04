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


        #self.tags = []

    #do only use before initialization!!!
    #after initialization use Netork.add_behaviours_to_neuron_group(...)
    def add_behaviour(self, index, b, init=False):
        self.behaviour[index] = copy.copy(b)
        if init:
            self.behaviour[index].set_variables(self)
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
        return self.get_buffer((self.size), buffer_size)

    def get_random_neuron_vec(self, density=1.0):
        return self.get_random_nparray((self.size), density)

    def get_shared_variables(self, name, avoid_None=True):
        result=[]
        for k in self.behaviour:
            val = self.behaviour[k].get_shared_variable(name)
            if val!=None or avoid_None==False:
                result.append(val)
        return np.array(result)

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



class TRENNeuronSubGroup:

    def __init__(self, BaseNeuronGroup, mask):
        self.BaseNeuronGroup = BaseNeuronGroup
        self.mask = mask

    def __getattr__(self, attr_name):
        if attr_name == 'BaseNeuronGroup' or attr_name == 'mask':
            return super().__getattr__(attr_name)#setattr

        if attr_name == 'size':
            return np.sum(self.mask)

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:
            if attr.shape[0] != self.mask.shape[0]:
                return attr[:, self.mask]
            else:
                return attr[self.mask]
        else:
            return attr

    def __setattr__(self, attr_name, value):
        if attr_name == 'BaseNeuronGroup' or attr_name == 'mask':
            super().__setattr__(attr_name, value)
            return

        attr = getattr(self.BaseNeuronGroup, attr_name)
        if type(attr) == np.ndarray:
            if attr.shape[0] != self.mask.shape[0]:
                attr[:, self.mask] = value
            else:
                attr[self.mask] = value
        else:
            setattr(self.BaseNeuronGroup, attr, value)

    def group_without_subGroup(self):
        return self.BaseNeuronGroup




