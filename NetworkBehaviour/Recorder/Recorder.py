from PymoNNto.NetworkCore.Behaviour import *
import copy

def get_Recorder(variable):
    return Recorder(variables=[variable])


class Recorder(Behaviour):
    visualization_module_outputs = []

    def __init__(self, variables, gapwidth=0, tag=None, max_length=None, save_as_numpy=False):
        super().__init__(tag=tag, variables=variables, gapwidth=gapwidth, max_length=max_length, save_as_numpy=save_as_numpy)
        #if tag is not None:
        #    self.add_tag(tag)
        self.add_tag('recorder')

        self.gapwidth = self.get_init_attr('gapwidth', 0)
        self.counter = 0
        self.new_data_available=False

        if type(variables) is str:
            variables=[variables]

        self.variables = {}
        self.compiled = {}
        self.save_as_numpy = self.get_init_attr('save_as_numpy', False)

        self.add_variables(self.get_init_attr('variables', []))
        self.reset()
        self.max_length = self.get_init_attr('max_length', None)

    def set_variables(self, neurons):
        self.reset()

    def add_varable(self, v):
        if self.save_as_numpy:
            self.variables[v] = np.array([])
        else:
            self.variables[v] = []
        self.compiled[v] = None

    def add_variables(self, vars):
        for v in vars:
            self.add_varable(v)

    def find_objects(self, key):
        result = []
        if key in self.variables:
            result.append(self.variables[key])
        return result

    def reset(self):
        for v in self.variables:
            self.add_varable(v)



    def is_new_data_available(self):
        if self.new_data_available:
            self.new_data_available = False
            return True
        else:
            return False

    def get_data_v(self, variable, parent_obj):
        n = parent_obj  # used for eval string "n.x"
        s = parent_obj
        neurons = parent_obj
        synapse = parent_obj

        return copy.copy(eval(self.compiled[variable]))

    def save_data_v(self, data, variable):
        if self.save_as_numpy:
            if len(self.variables[variable]) == 0:
                self.variables[variable] = np.array([data])
            else:
                self.variables[variable] = np.concatenate([self.variables[variable], [data]], axis=0)
        else:
            self.variables[variable].append(data)

    def new_iteration(self, parent_obj):
        if parent_obj.recording:

            self.counter += 1
            if self.counter >= self.gapwidth:
                self.new_data_available = True
                self.counter = 0
                for v in self.variables:
                    if self.compiled[v] is None:
                        self.compiled[v] = compile(v, '<string>', 'eval')
                    data = self.get_data_v(v, parent_obj)
                    if data is not None:
                        self.save_data_v(data, v)

        if self.max_length is not None:
            self.cut_length(self.max_length)

    def cut_length(self, max_length):
        if max_length is not None:
            for v in self.variables:
                while len(self.variables[v]) > max_length:
                    if self.save_as_numpy:
                        print('not implemented')
                    else:
                        self.variables[v].pop(0)

    def swaped(self, name):
        return self.swap(self.variables[name])#getattr(self, name)

    def swap(self, x):
        return np.swapaxes(np.array(x), 1, 0)

    def clear_recorder(self):
        print('clear')
        for v in self.variables:
            self.add_varable(v)

class EventRecorder(Recorder):

    def __init__(self, variables, tag=None):
        super().__init__(variables, gapwidth=0, tag=tag, max_length=None, save_as_numpy=True)

    def find_objects(self, key):

        result = []
        if key in self.variables:
            result.append(self.variables[key])

        if type(key) is str and key[-2:] == '.t' and key[:-2] in self.variables:
            result.append(self.variables[key[:-2]][:, 0])

        if type(key) is str and key[-2:] == '.i' and key[:-2] in self.variables:
            result.append(self.variables[key[:-2]][:, 1])

        return result

    def get_data_v(self, variable, parent_obj):
        n = parent_obj  # used for eval string "n.x"
        s = parent_obj
        neurons = parent_obj
        synapse = parent_obj

        data = eval(self.compiled[variable])
        indices = np.where(data != 0)[0]

        if len(indices) > 0:
            result = []
            for i in indices:
                result.append([parent_obj.iteration, i])
            return result
        else:
            return None

    def save_data_v(self, data, variable):
        if len(self.variables[variable]) == 0:
            self.variables[variable] = np.array(data)
        else:
            self.variables[variable] = np.concatenate([self.variables[variable], data], axis=0)

'''
class SynapseGroupRecorder(Recorder):

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









'''

class TRENRecorder(Neuron_Behaviour):

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


class TRENSynapseRecorder(TRENRecorder):

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
