from NetworkBehaviour.Logic.Basics.BasicHomeostasis import *

class STDP_base(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        #neurons.STDP_Function = self.get_init_attr('STDP_Function', [[1, 1.0]])
        #neurons.zerotime = self.get_init_attr('zerotime', 0)

        self.post_learn_value = self.get_init_attr('post_learn_value', 0.001, neurons)#0.003 better
        self.exponent = self.get_init_attr('exponent', 4.0, neurons)

        for s in neurons.afferent_synapses['GLU']:
            s.weight_change = s.get_synapse_mat()

        neurons.weight_change_sum=0#todo remove


    def new_iteration(self, neurons):
        if neurons.learning:
            weight_change_sum=0#todo remove
            for s in neurons.afferent_synapses['GLU']:
                s.weight_change *= 0

                #act_sum = s.get_dest_vec_obj(s.dst.output_activity_history[self.zerotime])[:]#output:auch lernen filtern / input:output filtern aber lernen nicht
                act_sum = s.dst.output_activity_history[self.zerotime][:]
                self.reward = np.clip(np.power(act_sum, self.exponent), 0, 1) * self.post_learn_value

                for STDP_t, STDP_y in self.STDP_Function:
                    pattern_at_t = s.src.output_activity_history[self.zerotime + STDP_t][:]
                    #pattern_at_t = s.get_src_vec_obj(s.src.output_activity_history[self.zerotime+STDP_t])[:]

                    s.weight_change += np.outer(self.reward * STDP_y, pattern_at_t)# * s.W_enabled

                s.weight_change *= s.enabled
                #weight_change_sum += np.sum(s.weight_change, axis=1)#todo remove

            #neurons.weight_change_sum = (neurons.weight_change_sum*100+weight_change_sum)/101#todo remove
            #print(neurons.weight_change_sum)

    def get_shared_variable(self, name):
        if name == 'buffer_size':
            return len(self.STDP_Function)+1

class STDP_simple(STDP_base):
    STDP_Function = [[1, 1.0]]
    zerotime=0#??? -1

class STDP_medium(STDP_base):
    STDP_Function = [[-1, -0.1], [0, 0.2], [1, 1.0]]
    zerotime=1

class STDP_complex(STDP_base):
    STDP_Function = [[-2, -0.1], [-1, -0.1], [0, 0.2], [1, 1.0], [2, 0.2]]
    zerotime=2


class TemporalWeightCache(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Weight_Cache')

        for s in neurons.afferent_synapses['GLU']:
            if not hasattr(s, 'weight_change'):
                s.weight_change = s.get_synapse_mat()

        self.decay = self.get_init_attr('decay', 1, neurons)
        self.strength = self.get_init_attr('strength', 1, neurons)

        if not hasattr(neurons, 'normalize'):
            neurons.normalize = np.array([self.get_init_attr('normalize', 1, neurons)])
        else:
            neurons.normalize = np.concatenate((neurons.normalize, np.array([self.get_init_attr('normalize', 1, neurons)])))

        self.GLU_density = self.get_init_attr('GLU_density', 1.0, neurons)
        self.GLU_random_factor = self.get_init_attr('GLU_random_factor', 1.0, neurons)
        self.GLU_equal_factor = self.get_init_attr('GLU_equal_factor', 0.0, neurons)
        all_neurons_same = self.get_init_attr('all_neurons_same', False, neurons)
        self.set_weights = self.get_init_attr('set_weights', False, neurons)

        for s in neurons.afferent_synapses['GLU']:

            if self.set_weights:
                #self.initialize_synapse_attr('W', self.GLU_density, 0.0, self.GLU_strength, neurons, 'GLU', all_neurons_same)
                s.enabled *= s.get_random_synapse_mat(self.GLU_density, all_neurons_same) > 0.0
                new_syn = s.enabled * (s.get_random_synapse_mat(1.0, all_neurons_same) * self.GLU_random_factor + self.GLU_equal_factor)
                #print(new_syn)
            else:
                new_syn = s.get_synapse_mat()#s.W.copy()

            if not hasattr(s, 'W_Caches'):
                self.cache_number = 0
                s.W_Caches = np.array([new_syn])
            else:
                self.cache_number = len(s.W_Caches)
                s.W_Caches = np.concatenate((s.W_Caches, np.array([new_syn])))


    def new_iteration(self, neurons):
        if neurons.learning:
            for s in neurons.afferent_synapses['GLU']:
                s.W_Caches[self.cache_number] = s.enabled*np.clip(s.W_Caches[self.cache_number]+s.weight_change*self.strength, 0, None)
                if self.decay != 0:
                    s.W_Caches[self.cache_number] *= self.decay

    def clear_weights(self, neurons):
        for s in neurons.afferent_synapses['GLU']:
            s.W_Caches[self.cache_number] *= 0


class RandomWeightFluctuation2(TemporalWeightCache):
    def set_variables(self, neurons):
        super().set_variables(neurons)
        for s in neurons.afferent_synapses['GLU']:
            s.W_Caches[self.cache_number]*=0
        #neurons.alpha = self.get_init_attr('alpha', 1)
        self.fluctuation = self.get_init_attr('fluctuation', 0.001, neurons)
        self.density = self.get_init_attr('density', 0.001, neurons)


    def new_iteration(self, neurons):
        if neurons.learning:
            for s in neurons.afferent_synapses['GLU']:
                s.W_Caches[self.cache_number] *= 0
                s.W_Caches[self.cache_number] += (s.get_random_synapse_mat(density=self.density))*self.fluctuation #only positive weight change
                #print(s.W_Caches[self.cache_number])
        super().new_iteration(neurons)


class DopamineProcessing(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.source_weight_id = self.get_init_attr('source_weight_id', 1, neurons)
        self.target_weight_id = self.get_init_attr('target_weight_id', 0, neurons)
        neurons.dopamine_level = 0

    def new_iteration(self, neurons):
        if neurons.learning:
            for s in neurons.afferent_synapses['GLU']:
                change = s.W_Caches[self.source_weight_id]*np.clip(neurons.dopamine_level, 0, 1)
                s.W_Caches[self.target_weight_id] += change
                s.W_Caches[self.source_weight_id] -= change

                #print(neurons.dopamine_level, np.sum(change))

            neurons.dopamine_level = 0

class RandomWeightFluctuation(TemporalWeightCache):
    def set_variables(self, neurons):
        super().set_variables(neurons)
        #neurons.alpha = self.get_init_attr('alpha', 1)
        self.beta = self.get_init_attr('beta', 1, neurons)
        self.gamma = self.get_init_attr('gamma', 1, neurons)


    def new_iteration(self, neurons):
        if neurons.learning:

            for s in neurons.afferent_synapses['GLU']:
                w = s.W.shape[0]
                h = s.W.shape[1]

                stable_weight=(s.W-s.W_Caches[self.cache_number])

                alpha_rnd = np.random.rand(w, h) * stable_weight * (self.beta - self.gamma)
                beta_rnd = np.random.rand(w, h) * self.beta
                gamma_rnd = np.random.rand(w, h) * self.gamma

                new_weight = s.W_Caches[self.cache_number] + (-beta_rnd+gamma_rnd) * s.W + alpha_rnd #+weight change?

                s.W_Caches[self.cache_number] = s.enabled*new_weight#np.clip(new_weight, 0, None)


