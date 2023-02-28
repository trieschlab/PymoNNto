from PymoNNto.NetworkCore.Behaviour import *
import copy

class Recorder(Behaviour):
    set_variables_last = True

    visualization_module_outputs = []

    def set_variables(self, parent_obj):
        self.add_tag('recorder')

        variables = self.parameter('variables', None)
        if variables is None:
            variables = self.parameter('arg_0', None)
            if variables is None:
                variables = []

        if type(variables) is str:
            variables = [variables]

        self.gapwidth = self.parameter('gapwidth', 0)
        self.save_as_numpy = self.parameter('save_as_numpy', False)
        self.max_length = self.parameter('max_length', None)
        self.counter = 0
        self.new_data_available=False
        self.variables = {}
        self.compiled = {}

        self.add_variables(variables)
        self.reset()

    def new_iteration(self, parent_obj):

        if parent_obj.recording:

            self.counter += 1
            if self.counter >= self.gapwidth:
                self.new_data_available = True
                self.counter = 0
                for v in self.variables:
                    if self.compiled[v] is None:
                        annotated_v = self.annotate_var_str(v, parent_obj)
                        self.compiled[v] = compile(annotated_v, '<string>', 'eval')
                    data = self.get_data_v(v, parent_obj)
                    if data is not None:
                        self.save_data_v(data, v)

        if self.max_length is not None:
            self.cut_length(self.max_length)

    def eq_split(self, eq, splitter):
        str = eq.replace(' ', '')
        parts = []
        str_buf = ''
        for s in str:
            if s in splitter:
                parts.append(str_buf)
                parts.append(s)
                str_buf = ''
            else:
                str_buf += s

        parts.append(str_buf)
        return parts

    def annotate_var_str(self, variable, parent_obj):
        splitter = ['*', '/', '+', '-', '%', ':', ';', '=', '!', '(', ')', '[', ']', '{', '}']
        annotated_var = ''
        for part in self.eq_split(variable, splitter):
            if hasattr(parent_obj, part):
                part = 'n.'+part
            annotated_var += part
        return annotated_var

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
        try:
            return copy.copy(eval(self.compiled[variable]))
        except:
            return None

    def save_data_v(self, data, variable):
        if self.save_as_numpy:
            if len(self.variables[variable]) == 0:
                self.variables[variable] = np.array([data])
            else:
                self.variables[variable] = np.concatenate([self.variables[variable], [data]], axis=0)
        else:
            self.variables[variable].append(data)



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

    def clear(self):
        self.clear_recorder()

    def clear_recorder(self):
        print('clear')

        for v in self.variables:
            self.variables[v].clear()


class EventRecorder(Recorder): #10: EventRecorder(tag='my_event_recorder', variables=['spike']) #plt.plot(My_Network['spike.t', 0], My_Network['spike.i', 0], '.k')

    def find_objects(self, key):

        result = []
        if key in self.variables:
            result.append(self.variables[key])

        if type(key) is str and key[-2:] == '.t' and key[:-2] in self.variables:#time
            result.append(self.variables[key[:-2]][:, 0])

        if type(key) is str and key[-2:] == '.i' and key[:-2] in self.variables:#neuron index
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

