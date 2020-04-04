from NetworkCore.Neuron_Group import *


class NeuronManualActivator(Neuron_Behaviour):

    #def __init__(self, clip_min=0.0, clip_max=1.0, write_to='glu_inter_gamma_activity'):
    #    self.clip_min = clip_min
    #    self.clip_max = clip_max
    #    self.write_to = write_to

    def set_variables(self, neurons):
        self.clip_min = self.get_init_attr('clip_min', 0.0, neurons)
        self.clip_max = self.get_init_attr('clip_max', 1.0, neurons)
        self.write_to = self.get_init_attr('write_to', 'glu_inter_gamma_activity', neurons)

        self.neurons=neurons
        neurons.outside_activation = neurons.get_neuron_vec()

        if not hasattr(neurons, self.write_to):
            setattr(neurons, self.write_to, neurons.get_neuron_vec())

    def new_iteration(self, neurons):
        getattr(neurons, self.write_to)[:] *= 0
        getattr(neurons, self.write_to)[:] += neurons.outside_activation
        getattr(neurons, self.write_to)[:] = np.clip(getattr(neurons, self.write_to)[:], self.clip_min, self.clip_max)
        neurons.outside_activation *= 0.0

    def activate(self, act, additive=False):
        if additive:
            self.neurons.outside_activation += np.array(act)
        else:
            self.neurons.outside_activation = np.array(act)


class NeuronActivator(Neuron_Behaviour):

    #def __init__(self, write_to='glu_inter_gamma_activity', pattern_groups=None, clip_min=0.0, clip_max=1.0):

    def find_objects(self, key):
        result = []
        for pg in self.TNAPatterns:
            result += pg[key]
        return result


    def set_variables(self, neurons):
        self.add_tag('activator')

        neurons.pattern_index = 0

        pattern_groups = self.get_init_attr('pattern_groups', None, neurons)

        self.clip_min = self.get_init_attr('clip_min', 0.0, neurons)
        self.clip_max = self.get_init_attr('clip_max', 1.0, neurons)
        self.write_to = self.get_init_attr('write_to', 'glu_inter_gamma_activity', neurons)

        setattr(neurons, self.write_to, neurons.get_neuron_vec())

        self.TNAPatterns = []

        self.active=True

        if pattern_groups is not None:
            self.add_patternGroups(pattern_groups, neurons)

        #self.neurons=neurons
        #if not hasattr(neurons, self.write_to):
        #    setattr(neurons, self.write_to, neurons.get_neuron_vec())

    def get_pattern_samples(self, number, size):
        result = []
        for i in range(number):
            result.append(self.get_pattern_values())
        return np.array(result)



    def get_pattern_values(self, neurons=None):
        patterns = []
        overlapping = np.zeros(neurons.size)

        if self.active:
            for pattern_group in self.TNAPatterns:

                if pattern_group.group_possibility >= 1.0 or np.random.rand() < pattern_group.group_possibility:
                    pat = pattern_group.get_pattern(neurons)
                    if pat is not None:
                        return pat
                else:
                    pat = None

                if pat is not None:
                    #if pat.shape is not (neurons.size,):
                    #    pat.resize((neurons.size), refcheck=False)
                    if pattern_group.overlapping_with_other_groups:
                        overlapping += pat
                    else:
                        if pattern_group.has_overlapping_priority:
                            return pat
                        else:
                            patterns.append(pat)

        patterns.append(overlapping)
        r = np.random.randint(len(patterns))
        return patterns[r]


    def new_iteration(self, neurons):
        #if self.active:
        #getattr(neurons, self.write_to)[:] *= 0 #todo test: moved from outside "if" block inside it
        getattr(neurons, self.write_to)[:] += self.get_pattern_values(neurons)
        neurons.pattern_index = self.TNAPatterns[0].current_pattern_index#todo: better
        #neurons.input_activity += self.get_pattern_values()
        #neurons.input_activity = np.clip(neurons.input_activity, self.clip_min, self.clip_max)#neccessary? multiple clipped

    def add_patternGroups(self, patterns, neurons):
        #if not hasattr(self, 'TNAPatterns'):
        #    self.TNAPatterns = []

        if type(patterns) == list:
            for p in patterns:
                self.TNAPatterns.append(p)
                p.initialize_neuron_group(neurons)
        else:
            self.TNAPatterns.append(patterns)
            patterns.initialize_neuron_group(neurons)





class NeuronPreprocessedActivator(NeuronActivator):

    def preprocess(self,preprocessing_steps, neurons):
        self.pattern_list = []
        for _ in range(preprocessing_steps):
            self.pattern_list.append(super().get_pattern_values(neurons))
            self.step = 0

    def reset(self):
        self.step = 0

    def get_pattern_values(self, neurons):
        self.step += 1
        if self.step<len(self.pattern_list):
            return self.pattern_list[self.step-1]
        else:
            return super().get_pattern_values(neurons)
