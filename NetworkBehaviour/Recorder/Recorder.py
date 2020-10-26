#from NetworkBehaviour.Logic.Images.Neuron_Homeostais import *
from NetworkBehaviour.Logic.Basics.BasicHomeostasis import *
#import compiler
import copy


class NeuronRecorder(Behaviour):

    def __init__(self, variables, gapwidth=0, tag=None, max_length=None):
        super().__init__()
        if tag is not None:
            self.add_tag(tag)
        self.add_tag('recorder')
        #self.init_kwargs={}
        self.gapwidth=gapwidth
        self.counter = 0
        self.new_data_available=False
        self.variables = {}
        self.compiled = {}

        for i, v in enumerate(variables):
            print(v)
        #    if v == 'np.mean(n.voltage)':
        #        variables[i] = 'np.mean(n.voltage.numpy())'

        self.add_variables(variables)
        self.reset()
        self.active=True
        self.max_length=max_length

    def add_varable(self, v):
        self.variables[v] = []
        self.compiled[v] = None

    def add_variables(self, vars):
        for v in vars:
            self.add_varable(v)

    #def __getitem__(self, key):
    #    return np.array(self.variables[key])

    def find_objects(self, key):
        result = []
        if key in self.variables:
            result.append(self.variables[key])
        return result

    def reset(self):
        for v in self.variables:
            self.variables[v] = []

    def set_variables(self, neurons):
        self.reset()

    def is_new_data_available(self):
        if self.new_data_available:
            self.new_data_available = False
            return True
        else:
            return False

    def new_iteration(self, neurons):
        if self.active and neurons.recording:
            n = neurons  # used for eval string "n.x"
            self.counter += 1
            if self.counter >= self.gapwidth:
                self.new_data_available=True
                self.counter = 0
                for v in self.variables:
                    if self.compiled[v] is None:
                        self.compiled[v] = compile(v, '<string>', 'eval')
                    self.variables[v].append(copy.copy(eval(self.compiled[v])))  # .copy()
        if self.max_length is not None:
            self.cut_length(self.max_length)

    def cut_length(self, max_length):
        if max_length is not None:
            for v in self.variables:
                while len(self.variables[v]) > max_length:
                    self.variables[v].pop(0)

    def swaped(self, name):
        return self.swap(getattr(self, name))

    def swap(self, x):
        return np.swapaxes(np.array(x), 1, 0)

    def clear_recorder(self):
        for v in self.variables:
            self.variables[v].clear()




class SynapseRecorder(NeuronRecorder):

    def __init__(self, variables, transmitter='GLU', gapwidth=0, tag=None, max_length=None):
        self.transmitter = transmitter
        super().__init__([], gapwidth, tag=tag, max_length=max_length)
        self.add_variables(variables)

    def find_objects(self, key):
        result = []
        k = self.get_synapse_command(key)
        if k in self.variables:
            result.append(self.variables[k])
        return result

    def add_variables(self, vars):
        super().add_variables([self.get_synapse_command(v) for v in vars])

    def get_synapse_command(self, var):
        return 'np.concatenate([' + var + ' for s in neurons.afferent_synapses.get("' + self.transmitter + '", np.array([]))], axis=1).flatten()'

    #def __getitem__(self, key):
    #    return np.array(self.variables[self.get_synapse_command(key)])










'''

class TRENNeuronRecorder(Neuron_Behaviour):

    def __init__(self, variables, behaviour_index=None, gapwidth=0):
        super().__init__()
        self.gapwidth=gapwidth
        self.counter = 0
        self.variables = []
        self.indexes = []
        for var in variables:
            var, indx = self.split_attribute_and_index(var)
            self.variables.append(var)
            self.indexes.append(indx)
        self.behaviour_index = behaviour_index
        self.reset()

    def reset(self):
        for var in self.variables:
            setattr(self, var, [])

    def set_variables(self, neurons):
        self.reset()

    def new_iteration(self, neurons):
        self.counter+=1
        if self.counter>self.gapwidth:
            self.counter=0
            src = neurons
            if self.behaviour_index is not None:
                src = neurons.behaviour[self.behaviour_index]

            for var, indx in zip(self.variables, self.indexes):
                val = getattr(src, var).copy()

                if indx is None:
                    getattr(self, var).append(val)
                else:
                    getattr(self, var).append(val[indx])

    def swaped(self, name):
        return self.swap(getattr(self, name))

    def swap(self, x):
        return np.swapaxes(np.array(x), 1, 0)

    def split_attribute_and_index(self, name):
        if '[' in name:
            split = name.split('[')
            return split[0], int(split[1][:-1])
        else:
            return [name, None]


class TRENSynapseRecorder(TRENNeuronRecorder):

    def __init__(self, transmitter, variables, gapwidth=0):
        super().__init__(variables, gapwidth)
        self.transmitter = transmitter

    def set_variables(self, neurons):
        super().set_variables(neurons)
        syns = neurons.afferent_synapses.get(self.transmitter, [])
        start = 0
        self.block_sizes = []
        for s in syns:
            size = s.get_dest_size()*s.get_src_size()
            end = start+size
            self.block_sizes.append([start, end])
            start=end

    def get_block_num(self):
        return len(self.block_sizes)

    def get_block(self, index, mat):
        return np.array(mat)[:, self.block_sizes[index][0]:self.block_sizes[index][1]]

    def new_iteration(self, neurons):
        self.counter+=1
        if self.counter>self.gapwidth:
            self.counter=0
            for var in self.variables:
                syns = neurons.afferent_synapses.get(self.transmitter, [])

                vals=np.array([])
                for s in syns:
                    vals = np.concatenate((vals, getattr(s, var).flatten()))

                getattr(self, var).append(vals)
                
'''
